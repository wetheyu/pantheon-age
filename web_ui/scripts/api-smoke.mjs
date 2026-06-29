const API_BASE_URL = (
  process.env.VITE_API_BASE_URL ||
  process.env.PANTHEON_API_BASE_URL ||
  "http://127.0.0.1:8000"
).replace(/\/$/, "");

const FINAL_DEMO_SETUP = {
  name: "伊芙",
  country_id: "lumiere",
  city: "卢塞恩",
  class_id: "rogue",
  god: "隐秘之神",
  background_id: "investigative_reporter",
};

async function fetchJson(path) {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`${path} failed with HTTP ${response.status}: ${await response.text()}`);
  }
  return response.json();
}

async function postJson(path, body) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error(`${path} failed with HTTP ${response.status}: ${await response.text()}`);
  }
  return response.json();
}

function requireArray(value, label) {
  if (!Array.isArray(value) || value.length === 0) {
    throw new Error(`${label} should be a non-empty array`);
  }
  return value;
}

async function run() {
  const [health, origins, classes, gods] = await Promise.all([
    fetchJson("/health"),
    fetchJson("/origins"),
    fetchJson("/classes"),
    fetchJson("/gods"),
  ]);

  const countries = requireArray(origins.countries, "origins.countries");
  const backgrounds = requireArray(origins.backgrounds, "origins.backgrounds");
  const classOptions = requireArray(classes.classes, "classes.classes");
  const godOptions = requireArray(gods.gods, "gods.gods");
  const country =
    countries.find((item) => item.country_id === FINAL_DEMO_SETUP.country_id) ||
    countries[0];
  const city =
    country.cities.find((item) => item.name === FINAL_DEMO_SETUP.city) ||
    requireArray(country.cities, "country.cities")[0];
  const background =
    backgrounds.find((item) => item.background_id === FINAL_DEMO_SETUP.background_id) ||
    backgrounds[0];
  const classOption =
    classOptions.find((item) => item.class_id === FINAL_DEMO_SETUP.class_id) ||
    classOptions[0];
  const god = godOptions.find((item) => item === FINAL_DEMO_SETUP.god) || godOptions[0];
  const ethnicity = Array.isArray(country.ethnicities) && country.ethnicities.length
    ? country.ethnicities[0].name
    : undefined;

  const game = await postJson("/games", {
    name: FINAL_DEMO_SETUP.name,
    class_id: classOption.class_id,
    god,
    game_mode: "world",
    origin_country_id: country.country_id,
    origin_city: city.name,
    origin_ethnicity: ethnicity,
    background_id: background.background_id,
  });

  if (!game.game_id || !game.state || !game.opening_text) {
    throw new Error("/games response is missing game_id, state, or opening_text");
  }

  const action = await postJson(`/games/${game.game_id}/actions`, {
    text: "观察周围，确认今晚异常传闻的来源",
    include_debug: false,
  });

  if (!action.story || !action.state || !action.mechanics) {
    throw new Error("/actions response is missing story, state, or mechanics");
  }

  console.log(
    `API smoke passed: ${health.version}, game=${game.game_id}, turn=${action.state.turn}`,
  );
}

run().catch((error) => {
  console.error(error instanceof Error ? error.message : error);
  process.exitCode = 1;
});
