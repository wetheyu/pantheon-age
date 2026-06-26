export type HealthResponse = {
  status: string;
  project: string;
  display_name: string;
  version: string;
};

export type ClassOption = {
  class_id: string;
  name: string;
  description?: string;
};

export type ClassesResponse = {
  classes: ClassOption[];
};

export type GodsResponse = {
  gods: string[];
};

export type OriginCity = {
  name: string;
  title: string;
  description: string;
};

export type OriginCountry = {
  country_id: string;
  name: string;
  formal_name: string;
  identity: string;
  summary: string;
  cities: OriginCity[];
  ethnicities: Array<{
    name: string;
    description: string;
  }>;
};

export type BackgroundOption = {
  background_id: string;
  name: string;
  description: string;
  wealth_level: number;
  wealth_label: string;
  resource_note: string;
};

export type ItemAffordance = {
  name: string;
  category: string;
  description: string;
  consumable: boolean;
  effects: Array<{
    risk_types: string[];
    check_stats: string[];
    bonus: number;
    consume: boolean;
  }>;
  direct_use: Record<string, unknown>;
};

export type OriginsResponse = {
  countries: OriginCountry[];
  backgrounds: BackgroundOption[];
};

export type ApiBootData = {
  health: HealthResponse;
  classes: ClassesResponse;
  gods: GodsResponse;
  origins: OriginsResponse;
};

export type GameCreateRequest = {
  name: string;
  class_id: string;
  god: string;
  game_mode: "world";
  origin_country_id: string;
  origin_city: string;
  origin_ethnicity?: string;
  background_id: string;
};

export type PublicGameState = {
  turn: number;
  current_location: string;
  current_scene_focus: string;
  available_exits: string[];
  game_mode: string;
  scenario_id: string;
  is_world_mode: boolean;
  is_game_over: boolean;
  ending_id?: string | null;
  ending_text: string;
  visited_locations: string[];
  event_log: string[];
  core_clue_count: number;
  core_clue_total: number;
  player: {
    name: string;
    class_id: string;
    class_name: string;
    god: string;
    stats: Record<string, number>;
    attributes: Record<string, number>;
    hp: number;
    max_hp: number;
    san: number;
    max_san: number;
    suspicion: number;
    corruption: number;
    inventory: string[];
    item_affordances: ItemAffordance[];
    skills: string[];
    current_location: string;
    clues: string[];
    origin: {
      country_id: string;
      country: string;
      formal_name: string;
      identity: string;
      ethnicity: string;
      city: string;
      city_title: string;
      background_id: string;
      background_name: string;
      background_description: string;
      wealth_level: number;
      wealth_label: string;
      resource_note: string;
      church_context: Record<string, unknown>;
      current_scene_focus: string;
      opening_profile: Record<string, unknown>;
    };
    progression: {
      class_level: number;
      faith_level: number;
      ascension_rank: number;
      revelation: number;
      favor: number;
      devotion: number;
      progression_skills: string[];
      skill_affordances: Array<Record<string, unknown>>;
      talents: string[];
      talent_affordances: Array<Record<string, unknown>>;
      prayers: string[];
      prayer_affordances: Array<Record<string, unknown>>;
      burdens: string[];
      progression_flags: Record<string, unknown>;
      advancement_options: Array<Record<string, unknown>>;
    };
  };
};

export type GameCreateResponse = {
  game_id: string;
  state: PublicGameState;
  opening_text: string;
  game_mode: string;
  setup: Record<string, unknown>;
};

export type ActionRequest = {
  text: string;
  include_debug?: boolean;
};

export type ActionMechanics = {
  kind: string;
  consumes_turn: boolean;
  roll?: Record<string, unknown> | null;
  committed_effects: unknown[];
  state_changes: unknown[];
  new_clues: unknown[];
};

export type ActionResponse = {
  game_id: string;
  response: Record<string, unknown>;
  story: string;
  state: PublicGameState;
  mechanics: ActionMechanics;
  debug?: Record<string, unknown> | null;
};
