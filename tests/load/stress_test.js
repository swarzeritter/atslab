/**
 * Stress test — Variant 2
 * Measures maximum RPS separately for: login, view post, create post, add comment.
 *
 * Usage (run from Project directory):
 *   k6 run --env SCENARIO=login    tests/load/stress_test.js
 *   k6 run --env SCENARIO=view     tests/load/stress_test.js
 *   k6 run --env SCENARIO=create   tests/load/stress_test.js
 *   k6 run --env SCENARIO=comment  tests/load/stress_test.js
 *
 * Stages: 30s warmup → 1m ramp → 1m plateau → 30s ramp-down
 */
import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = 'http://127.0.0.1:8000';
const EMAIL    = 'stress1@test.com';
const PASSWORD = 'stresspass123';

// ---------------------------------------------------------------------------
// Executor config shared by all scenarios
// ---------------------------------------------------------------------------
const STAGES = [
  { duration: '30s', target: 1  },  // warmup
  { duration: '1m',  target: 10 },  // ramp up
  { duration: '1m',  target: 25 },  // plateau
  { duration: '30s', target: 0  },  // ramp down
];

const scenarioName = __ENV.SCENARIO || 'login';

export const options = {
  scenarios: {
    stress: {
      executor: 'ramping-arrival-rate',
      startRate: 1,
      timeUnit: '1s',
      preAllocatedVUs: 30,
      maxVUs: 100,
      stages: STAGES,
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<3000'],
    http_req_failed:   ['rate<0.10'],
  },
};

// ---------------------------------------------------------------------------
// Setup: login once and return session cookie + post ID
// ---------------------------------------------------------------------------
export function setup() {
  const loginRes = http.post(`${BASE_URL}/auth/login`, {
    email: EMAIL, password: PASSWORD,
  }, { redirects: 0 });

  const cookie = loginRes.cookies['access_token']
    ? loginRes.cookies['access_token'][0].value
    : '';

  // Get first post ID
  const listRes = http.get(`${BASE_URL}/posts`, {
    headers: { Cookie: `access_token=${cookie}` },
  });
  const match = listRes.body.match(/href="\/posts\/(\d+)"/);
  const postId = match ? match[1] : '1';

  http.get(`${BASE_URL}/auth/logout`, {
    headers: { Cookie: `access_token=${cookie}` },
  });

  return { postId };
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function loginAndGetCookie() {
  const res = http.post(`${BASE_URL}/auth/login`, {
    email: EMAIL, password: PASSWORD,
  }, { redirects: 0 });
  check(res, { 'login 303': (r) => r.status === 303 });
  const cookie = res.cookies['access_token'];
  return cookie ? cookie[0].value : '';
}

function authHeaders(cookie) {
  return { headers: { Cookie: `access_token=${cookie}` } };
}

// ---------------------------------------------------------------------------
// Default function — dispatches to chosen scenario
// ---------------------------------------------------------------------------
export default function (data) {
  if (scenarioName === 'login') {
    runLogin();
  } else if (scenarioName === 'view') {
    runViewPost(data);
  } else if (scenarioName === 'create') {
    runCreatePost();
  } else if (scenarioName === 'comment') {
    runAddComment(data);
  }
}

// ---------------------------------------------------------------------------
// Scenario A: Login
// ---------------------------------------------------------------------------
function runLogin() {
  const res = http.post(`${BASE_URL}/auth/login`, {
    email: EMAIL, password: PASSWORD,
  }, { redirects: 0 });

  check(res, {
    'login: status 303':       (r) => r.status === 303,
    'login: sets cookie':      (r) => !!r.cookies['access_token'],
  });

  // Logout to keep DB clean (clear session)
  if (res.cookies['access_token']) {
    http.get(`${BASE_URL}/auth/logout`, authHeaders(res.cookies['access_token'][0].value));
  }
}

// ---------------------------------------------------------------------------
// Scenario B: View post
// ---------------------------------------------------------------------------
function runViewPost(data) {
  const cookie = loginAndGetCookie();

  const res = http.get(`${BASE_URL}/posts/${data.postId}`, authHeaders(cookie));
  check(res, { 'view post: status 200': (r) => r.status === 200 });

  http.get(`${BASE_URL}/auth/logout`, authHeaders(cookie));
}

// ---------------------------------------------------------------------------
// Scenario C: Create post
// ---------------------------------------------------------------------------
function runCreatePost() {
  const cookie = loginAndGetCookie();

  const res = http.post(`${BASE_URL}/posts`, {
    title:   `Stress post ${Date.now()}`,
    content: 'Created during stress test.',
  }, { ...authHeaders(cookie), redirects: 0 });

  check(res, { 'create post: status 303': (r) => r.status === 303 });

  http.get(`${BASE_URL}/auth/logout`, authHeaders(cookie));
}

// ---------------------------------------------------------------------------
// Scenario D: Add comment
// ---------------------------------------------------------------------------
function runAddComment(data) {
  const cookie = loginAndGetCookie();

  const res = http.post(
    `${BASE_URL}/posts/${data.postId}/comments`,
    { content: `Stress comment ${Date.now()}` },
    { ...authHeaders(cookie), redirects: 0 }
  );
  check(res, { 'add comment: status 303': (r) => r.status === 303 });

  http.get(`${BASE_URL}/auth/logout`, authHeaders(cookie));
}
