import React, { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { API_BASE_URL, createWorldGame, loadBootData, submitGameAction } from "./api";
import type {
  ActionMechanics,
  ApiBootData,
  BackgroundOption,
  GameCreateResponse,
  ItemAffordance,
  OriginCountry,
  PublicGameState,
} from "./types";
import "./styles.css";

type LoadState =
  | { status: "loading" }
  | { status: "ready"; data: ApiBootData }
  | { status: "error"; message: string };

type CreateState =
  | { status: "idle" }
  | { status: "submitting" }
  | { status: "created"; game: GameCreateResponse }
  | { status: "error"; message: string };

type StoryEntry = {
  id: string;
  role: "host" | "player" | "system";
  text: string;
  mechanics?: ActionMechanics;
};

const ATTRIBUTE_LABELS: Record<string, string> = {
  physique: "体魄",
  agility: "灵巧",
  insight: "洞察",
  knowledge: "学识",
  will: "意志",
  communion: "共鸣",
};

const LEGACY_STAT_LABELS: Record<string, string> = {
  strength: "力量",
  agility: "敏捷",
  intelligence: "智力",
  faith: "信仰",
};

function App() {
  const [loadState, setLoadState] = useState<LoadState>({ status: "loading" });

  useEffect(() => {
    let isMounted = true;

    loadBootData()
      .then((data) => {
        if (isMounted) {
          setLoadState({ status: "ready", data });
        }
      })
      .catch((error: unknown) => {
        if (isMounted) {
          setLoadState({
            status: "error",
            message: error instanceof Error ? error.message : "未知连接错误",
          });
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <main className="app-shell">
      <header className="top-bar">
        <div>
          <p className="eyebrow">Pantheon Age Web</p>
          <h1>神座纪元</h1>
        </div>
        <ConnectionBadge state={loadState} />
      </header>

      <section className="workspace">
        <section className="story-panel">
          <p className="eyebrow">Phase 9.6</p>
          <h2>创建角色并试玩第一幕</h2>
          <p>
            在浏览器里创建 world-mode 游戏，然后像跑团一样输入行动。前端只负责提交文字和展示返回结果；
            裁定、叙事、掷骰、记忆和状态修改仍由后端运行时负责。
          </p>
          <dl className="api-list">
            <div>
              <dt>API 地址</dt>
              <dd>{API_BASE_URL}</dd>
            </div>
            <div>
              <dt>本阶段接口</dt>
              <dd>/origins, /classes, /gods, /games, /games/:id/actions</dd>
            </div>
          </dl>
        </section>

        {loadState.status === "loading" && <LoadingPanel />}
        {loadState.status === "error" && <ErrorPanel message={loadState.message} />}
        {loadState.status === "ready" && <CharacterCreation data={loadState.data} />}
      </section>
    </main>
  );
}

function ConnectionBadge({ state }: { state: LoadState }) {
  if (state.status === "ready") {
    return <span className="status-badge success">API 已连接</span>;
  }
  if (state.status === "error") {
    return <span className="status-badge error">API 未连接</span>;
  }
  return <span className="status-badge">连接中</span>;
}

function LoadingPanel() {
  return (
    <section className="panel muted-panel">
      <h2>正在读取后端数据</h2>
      <p>请确认 FastAPI 正在运行。</p>
    </section>
  );
}

function ErrorPanel({ message }: { message: string }) {
  return (
    <section className="panel error-panel">
      <h2>无法连接 API</h2>
      <p>{message}</p>
      <p>先运行 `./.venv/bin/uvicorn phase2_api.main:app`，再刷新本页面。</p>
    </section>
  );
}

function CharacterCreation({ data }: { data: ApiBootData }) {
  const firstCountry = data.origins.countries[0];
  const firstClass = data.classes.classes[0];
  const firstGod = data.gods.gods[0];
  const firstBackground = data.origins.backgrounds[0];

  const [playerName, setPlayerName] = useState("伊芙");
  const [selectedCountryId, setSelectedCountryId] = useState(firstCountry?.country_id ?? "");
  const [selectedCity, setSelectedCity] = useState(firstCountry?.cities[0]?.name ?? "");
  const [selectedEthnicity, setSelectedEthnicity] = useState(
    firstCountry?.ethnicities[0]?.name ?? "",
  );
  const [selectedClassId, setSelectedClassId] = useState(firstClass?.class_id ?? "");
  const [selectedGod, setSelectedGod] = useState(firstGod ?? "");
  const [selectedBackgroundId, setSelectedBackgroundId] = useState(
    firstBackground?.background_id ?? "",
  );
  const [createState, setCreateState] = useState<CreateState>({ status: "idle" });

  const selectedCountry = useMemo(
    () => data.origins.countries.find((country) => country.country_id === selectedCountryId),
    [data.origins.countries, selectedCountryId],
  );

  const selectedBackground = useMemo(
    () =>
      data.origins.backgrounds.find(
        (background) => background.background_id === selectedBackgroundId,
      ),
    [data.origins.backgrounds, selectedBackgroundId],
  );

  const selectedClass = useMemo(
    () => data.classes.classes.find((item) => item.class_id === selectedClassId),
    [data.classes.classes, selectedClassId],
  );

  function handleCountryChange(countryId: string) {
    const nextCountry = data.origins.countries.find((country) => country.country_id === countryId);
    setSelectedCountryId(countryId);
    setSelectedCity(nextCountry?.cities[0]?.name ?? "");
    setSelectedEthnicity(nextCountry?.ethnicities[0]?.name ?? "");
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedCountry || !selectedCity || !selectedClassId || !selectedGod || !selectedBackgroundId) {
      setCreateState({ status: "error", message: "请先补齐角色创建选项。" });
      return;
    }

    setCreateState({ status: "submitting" });
    try {
      const game = await createWorldGame({
        name: playerName.trim() || "无名调查者",
        class_id: selectedClassId,
        god: selectedGod,
        game_mode: "world",
        origin_country_id: selectedCountry.country_id,
        origin_city: selectedCity,
        origin_ethnicity: selectedEthnicity || undefined,
        background_id: selectedBackgroundId,
      });
      setCreateState({ status: "created", game });
    } catch (error: unknown) {
      setCreateState({
        status: "error",
        message: error instanceof Error ? error.message : "创建游戏失败",
      });
    }
  }

  function handleNewGame() {
    setCreateState({ status: "idle" });
  }

  return (
    <section className="creation-grid">
      <form className="panel creation-form" onSubmit={handleSubmit}>
        <p className="eyebrow">角色创建</p>
        <h2>开局设置</h2>

        <label className="field">
          <span>名字</span>
          <input value={playerName} onChange={(event) => setPlayerName(event.target.value)} />
        </label>

        <label className="field">
          <span>出身国家</span>
          <select
            value={selectedCountryId}
            onChange={(event) => handleCountryChange(event.target.value)}
          >
            {data.origins.countries.map((country) => (
              <option key={country.country_id} value={country.country_id}>
                {country.name}
              </option>
            ))}
          </select>
        </label>

        <label className="field">
          <span>开局城市</span>
          <select value={selectedCity} onChange={(event) => setSelectedCity(event.target.value)}>
            {selectedCountry?.cities.map((city) => (
              <option key={city.name} value={city.name}>
                {city.name}
                {city.title ? ` · ${city.title}` : ""}
              </option>
            ))}
          </select>
        </label>

        {selectedCountry && selectedCountry.ethnicities.length > 0 && (
          <label className="field">
            <span>民族</span>
            <select
              value={selectedEthnicity}
              onChange={(event) => setSelectedEthnicity(event.target.value)}
            >
              {selectedCountry.ethnicities.map((ethnicity) => (
                <option key={ethnicity.name} value={ethnicity.name}>
                  {ethnicity.name}
                </option>
              ))}
            </select>
          </label>
        )}

        <label className="field">
          <span>职业</span>
          <select
            value={selectedClassId}
            onChange={(event) => setSelectedClassId(event.target.value)}
          >
            {data.classes.classes.map((item) => (
              <option key={item.class_id} value={item.class_id}>
                {item.name}
              </option>
            ))}
          </select>
        </label>

        <label className="field">
          <span>信仰</span>
          <select value={selectedGod} onChange={(event) => setSelectedGod(event.target.value)}>
            {data.gods.gods.map((god) => (
              <option key={god} value={god}>
                {god}
              </option>
            ))}
          </select>
        </label>

        <label className="field">
          <span>身份背景</span>
          <select
            value={selectedBackgroundId}
            onChange={(event) => setSelectedBackgroundId(event.target.value)}
          >
            {data.origins.backgrounds.map((background) => (
              <option key={background.background_id} value={background.background_id}>
                {background.name}
              </option>
            ))}
          </select>
        </label>

        <button className="primary-action" disabled={createState.status === "submitting"} type="submit">
          {createState.status === "submitting" ? "正在创建..." : "创建游戏"}
        </button>

        {createState.status === "error" && <p className="form-error">{createState.message}</p>}
      </form>

      <section className="preview-stack">
        <OriginPreview country={selectedCountry} background={selectedBackground} />
        <RolePreview classNameText={selectedClass?.name} god={selectedGod} />
        <CreatedGamePanel state={createState} onNewGame={handleNewGame} />
      </section>
    </section>
  );
}

function OriginPreview({
  country,
  background,
}: {
  country?: OriginCountry;
  background?: BackgroundOption;
}) {
  if (!country) {
    return null;
  }

  return (
    <article className="panel">
      <p className="eyebrow">出身预览</p>
      <h2>{country.formal_name}</h2>
      <p>{country.summary}</p>
      <div className="city-grid compact">
        {country.cities.map((city) => (
          <section className="city-card" key={city.name}>
            <h4>
              {city.name}
              {city.title ? <span>{city.title}</span> : null}
            </h4>
            <p>{city.description}</p>
          </section>
        ))}
      </div>
      {background && (
        <section className="selected-background">
          <h3>{background.name}</h3>
          <p>{background.description}</p>
          <small>
            资源：{background.wealth_label} · {background.resource_note}
          </small>
        </section>
      )}
    </article>
  );
}

function RolePreview({ classNameText, god }: { classNameText?: string; god: string }) {
  return (
    <article className="panel">
      <p className="eyebrow">角色方向</p>
      <h2>
        {classNameText || "未知职业"} / {god || "未知信仰"}
      </h2>
      <p>
        职业、信仰、属性、祷告和资源边界会由后端创建角色时写入状态。浏览器这里只展示你即将提交的选择。
      </p>
    </article>
  );
}

function CreatedGamePanel({
  state,
  onNewGame,
}: {
  state: CreateState;
  onNewGame: () => void;
}) {
  if (state.status === "idle") {
    return (
      <article className="panel muted-panel">
        <p className="eyebrow">开场</p>
        <h2>等待创建游戏</h2>
        <p>创建后，这里会显示开场叙事，并出现行动输入框。</p>
      </article>
    );
  }

  if (state.status === "submitting") {
    return (
      <article className="panel muted-panel">
        <p className="eyebrow">开场</p>
        <h2>主持人正在准备第一幕</h2>
        <p>正在创建 world-mode 游戏会话...</p>
      </article>
    );
  }

  if (state.status === "error") {
    return (
      <article className="panel error-panel">
        <p className="eyebrow">开场</p>
        <h2>创建失败</h2>
        <p>{state.message}</p>
      </article>
    );
  }

  const game = state.game;
  return <PlaySurface initialGame={game} key={game.game_id} onNewGame={onNewGame} />;
}

function PlaySurface({
  initialGame,
  onNewGame,
}: {
  initialGame: GameCreateResponse;
  onNewGame: () => void;
}) {
  const player = initialGame.state.player;
  const logRef = useRef<HTMLDivElement | null>(null);
  const [currentState, setCurrentState] = useState(initialGame.state);
  const [entries, setEntries] = useState<StoryEntry[]>([
    {
      id: "opening",
      role: "host",
      text: initialGame.opening_text,
    },
  ]);
  const [inputText, setInputText] = useState("");
  const [suggestions, setSuggestions] = useState(suggestedActionsFromState(initialGame.state));
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const isGameOver = currentState.is_game_over;

  useEffect(() => {
    logRef.current?.scrollTo({
      top: logRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [entries, isSubmitting]);

  async function handleActionSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const text = inputText.trim();
    if (!text || isSubmitting || isGameOver) {
      return;
    }

    setInputText("");
    setErrorMessage("");
    setIsSubmitting(true);
    setEntries((current) => [
      ...current,
      {
        id: `player-${Date.now()}`,
        role: "player",
        text,
      },
    ]);

    try {
      const result = await submitGameAction(initialGame.game_id, {
        text,
        include_debug: false,
      });
      setCurrentState(result.state);
      const nextSuggestions = suggestedActionsFromState(result.state);
      if (nextSuggestions.length) {
        setSuggestions(nextSuggestions);
      }
      setEntries((current) => [
        ...current,
        {
          id: `host-${Date.now()}`,
          role: "host",
          text: result.story,
          mechanics: result.mechanics,
        },
      ]);
    } catch (error: unknown) {
      setErrorMessage(error instanceof Error ? error.message : "行动提交失败");
      setEntries((current) => [
        ...current,
        {
          id: `system-${Date.now()}`,
          role: "system",
          text: "行动提交失败。请确认 API 仍在运行，然后重试。",
        },
      ]);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="active-game-grid">
      <article className="panel opening-panel">
        <div className="game-heading">
          <div>
            <p className="eyebrow">游戏已创建</p>
            <h2>{player.name} 的第一幕</h2>
          </div>
          <button className="secondary-action" onClick={onNewGame} type="button">
            新建角色
          </button>
        </div>
        <dl className="game-meta">
          <div>
            <dt>Game ID</dt>
            <dd>{initialGame.game_id}</dd>
          </div>
          <div>
            <dt>位置</dt>
            <dd>
              {currentState.current_location} / {currentState.current_scene_focus}
            </dd>
          </div>
          <div>
            <dt>回合</dt>
            <dd>{currentState.turn}</dd>
          </div>
          <div>
            <dt>身份</dt>
            <dd>
              {player.origin.formal_name} · {player.origin.background_name}
            </dd>
          </div>
        </dl>

        <div className="story-log" ref={logRef}>
          {entries.map((entry) => (
            <StoryBubble entry={entry} key={entry.id} />
          ))}
          {isSubmitting && (
            <div className="story-entry host">
              <p className="speaker">主持人</p>
              <p>主持人正在思考...</p>
            </div>
          )}
        </div>

        {isGameOver && <GameEndNotice state={currentState} />}

        {!isGameOver && suggestions.length > 0 && (
          <QuickActions
            disabled={isSubmitting}
            suggestions={suggestions}
            onSelect={(text) => setInputText(text)}
          />
        )}

        <form className={`action-form${isGameOver ? " disabled" : ""}`} onSubmit={handleActionSubmit}>
          <label className="field">
            <span>你的行动</span>
            <textarea
              disabled={isSubmitting || isGameOver}
              placeholder="例如：去码头账房查昨晚的船只记录"
              rows={3}
              value={inputText}
              onChange={(event) => setInputText(event.target.value)}
            />
          </label>
          <button
            className="primary-action"
            disabled={isSubmitting || isGameOver || !inputText.trim()}
            type="submit"
          >
            {isGameOver ? "游戏已结束" : isSubmitting ? "主持人思考中..." : "提交行动"}
          </button>
          {errorMessage && <p className="form-error">{errorMessage}</p>}
        </form>
      </article>

      <GameStatePanels state={currentState} />
    </section>
  );
}

function suggestedActionsFromState(state: PublicGameState) {
  const value = state.player.origin.opening_profile?.suggested_actions;
  if (!Array.isArray(value)) {
    return [];
  }
  return value.filter((item): item is string => typeof item === "string" && item.trim().length > 0);
}

function QuickActions({
  suggestions,
  disabled,
  onSelect,
}: {
  suggestions: string[];
  disabled: boolean;
  onSelect: (text: string) => void;
}) {
  return (
    <section className="quick-actions">
      <p>行动建议</p>
      <div className="quick-action-list">
        {suggestions.slice(0, 4).map((suggestion) => (
          <button
            className="quick-action"
            disabled={disabled}
            key={suggestion}
            onClick={() => onSelect(suggestion)}
            type="button"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </section>
  );
}

function GameEndNotice({ state }: { state: PublicGameState }) {
  return (
    <section className="ending-notice">
      <p className="eyebrow">结局</p>
      <h3>{state.ending_id || "游戏已结束"}</h3>
      <p>{state.ending_text || "本局已经结束。可以新建角色开始下一局。"}</p>
    </section>
  );
}

function StoryBubble({ entry }: { entry: StoryEntry }) {
  return (
    <div className={`story-entry ${entry.role}`}>
      <p className="speaker">{entry.role === "player" ? "你" : entry.role === "system" ? "系统" : "主持人"}</p>
      <div className="story-text">
        {entry.text.split("\n").map((line, index) => (
          <p key={`${entry.id}-${index}`}>{line}</p>
        ))}
      </div>
      {entry.mechanics && <MechanicsSummary mechanics={entry.mechanics} />}
    </div>
  );
}

function MechanicsSummary({ mechanics }: { mechanics: ActionMechanics }) {
  const committed = formatMechanicsList(mechanics.committed_effects);
  const changes = formatMechanicsList(mechanics.state_changes);
  const roll = mechanics.roll ? "有检定" : "无检定";

  return (
    <dl className="mechanics-summary">
      <div>
        <dt>回合</dt>
        <dd>{mechanics.consumes_turn ? "消耗" : "不消耗"}</dd>
      </div>
      <div>
        <dt>掷骰</dt>
        <dd>{roll}</dd>
      </div>
      <div>
        <dt>提交效果</dt>
        <dd>{committed}</dd>
      </div>
      <div>
        <dt>状态变化</dt>
        <dd>{changes}</dd>
      </div>
    </dl>
  );
}

function formatMechanicsList(items: unknown[]) {
  if (!items.length) {
    return "无";
  }
  return items
    .map((item) => {
      if (typeof item === "string") {
        return item;
      }
      return JSON.stringify(item);
    })
    .join("、");
}

function GameStatePanels({ state }: { state: PublicGameState }) {
  const player = state.player;
  const progression = player.progression;

  return (
    <aside className="state-panels">
      <section className="panel state-card">
        <p className="eyebrow">角色</p>
        <h2>{player.name}</h2>
        <p>
          {player.class_name} / {player.god}
        </p>
        <p>
          {player.origin.formal_name} · {player.origin.ethnicity} · {player.origin.background_name}
        </p>
        <p className="resource-note">{player.origin.resource_note}</p>
      </section>

      <section className="panel state-card">
        <p className="eyebrow">状态</p>
        <VitalBar label="HP" value={player.hp} max={player.max_hp} />
        <VitalBar label="SAN" value={player.san} max={player.max_san} />
        <dl className="compact-stats">
          <div>
            <dt>Suspicion</dt>
            <dd>{player.suspicion}</dd>
          </div>
          <div>
            <dt>Corruption</dt>
            <dd>{player.corruption}</dd>
          </div>
        </dl>
      </section>

      <section className="panel state-card">
        <p className="eyebrow">位置</p>
        <h2>{state.current_location}</h2>
        <p>{state.current_scene_focus}</p>
        <p>已访问：{state.visited_locations.length ? state.visited_locations.join("、") : "暂无"}</p>
      </section>

      <section className="panel state-card">
        <p className="eyebrow">六属性</p>
        <AttributeGrid values={player.attributes} labels={ATTRIBUTE_LABELS} />
      </section>

      <section className="panel state-card">
        <p className="eyebrow">旧四维</p>
        <AttributeGrid values={player.stats} labels={LEGACY_STAT_LABELS} />
      </section>

      <section className="panel state-card">
        <p className="eyebrow">成长</p>
        <dl className="compact-stats">
          <div>
            <dt>职业等级</dt>
            <dd>{progression.class_level}</dd>
          </div>
          <div>
            <dt>信仰等级</dt>
            <dd>{progression.faith_level}</dd>
          </div>
          <div>
            <dt>神秘阶位</dt>
            <dd>{progression.ascension_rank}</dd>
          </div>
          <div>
            <dt>Revelation</dt>
            <dd>{progression.revelation}</dd>
          </div>
          <div>
            <dt>Favor</dt>
            <dd>{progression.favor}</dd>
          </div>
          <div>
            <dt>Devotion</dt>
            <dd>{progression.devotion}</dd>
          </div>
        </dl>
        <TagList title="技能" items={progression.progression_skills} />
        <TagList title="天赋" items={progression.talents} />
        <TagList title="祷告" items={progression.prayers} />
        <TagList title="负担" items={progression.burdens} emptyText="暂无" />
      </section>

      <section className="panel state-card">
        <p className="eyebrow">背包</p>
        {player.item_affordances.length ? (
          <div className="item-list">
            {player.item_affordances.map((item) => (
              <ItemCard item={item} key={item.name} />
            ))}
          </div>
        ) : (
          <p>暂无物品</p>
        )}
      </section>

      <section className="panel state-card">
        <p className="eyebrow">线索</p>
        <p>
          核心线索：{state.core_clue_count}/{state.core_clue_total}
        </p>
        <TagList title="已知线索" items={player.clues} emptyText="暂无" />
      </section>
    </aside>
  );
}

function VitalBar({ label, value, max }: { label: string; value: number; max: number }) {
  const percent = max > 0 ? Math.max(0, Math.min(100, (value / max) * 100)) : 0;
  return (
    <div className="vital">
      <div className="vital-label">
        <span>{label}</span>
        <strong>
          {value}/{max}
        </strong>
      </div>
      <div className="vital-track">
        <div className="vital-fill" style={{ width: `${percent}%` }} />
      </div>
    </div>
  );
}

function AttributeGrid({
  values,
  labels,
}: {
  values: Record<string, number>;
  labels: Record<string, string>;
}) {
  return (
    <dl className="attribute-grid">
      {Object.entries(values).map(([key, value]) => (
        <div key={key}>
          <dt>{labels[key] ?? key}</dt>
          <dd>{value}</dd>
        </div>
      ))}
    </dl>
  );
}

function TagList({
  title,
  items,
  emptyText = "暂无",
}: {
  title: string;
  items: string[];
  emptyText?: string;
}) {
  return (
    <div className="tag-section">
      <h3>{title}</h3>
      {items.length ? (
        <div className="chip-list compact">
          {items.map((item) => (
            <span className="chip subtle" key={item}>
              {item}
            </span>
          ))}
        </div>
      ) : (
        <p>{emptyText}</p>
      )}
    </div>
  );
}

function ItemCard({ item }: { item: ItemAffordance }) {
  const effects = item.effects
    .map((effect) => {
      const risk = effect.risk_types.join("/");
      const stats = effect.check_stats.join("/");
      return `${risk || "通用"} ${stats || ""} +${effect.bonus}${effect.consume ? " 消耗" : ""}`;
    })
    .filter(Boolean);

  return (
    <section className="item-card">
      <h3>
        {item.name}
        {item.consumable ? <span>消耗品</span> : <span>{item.category}</span>}
      </h3>
      <p>{item.description || "暂无描述"}</p>
      {effects.length ? <small>{effects.join("；")}</small> : null}
    </section>
  );
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
