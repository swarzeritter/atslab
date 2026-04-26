import http from 'k6/http';
import { check, sleep, group } from 'k6';

const BASE_URL = 'http://127.0.0.1:8000';
const USERNAME = 'k6testuser';
const EMAIL = 'k6test@test.com';
const PASSWORD = 'k6test123';

export const options = {
  scenarios: {
    view_post: {
      executor: 'constant-vus',
      vus: 2,
      duration: '30s',
      exec: 'viewPost',
    },
    comment_on_post: {
      executor: 'constant-vus',
      vus: 1,
      duration: '30s',
      exec: 'commentOnPost',
    },
    create_post: {
      executor: 'constant-vus',
      vus: 1,
      duration: '30s',
      exec: 'createPost',
    },
    edit_profile: {
      executor: 'constant-vus',
      vus: 1,
      duration: '30s',
      exec: 'editProfile',
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<1000', 'p(99)<2000'],
    http_req_failed: ['rate<0.05'],
  },
};

// ---------------------------------------------------------------------------
// Setup: register test user and create a post to use in scenarios
// ---------------------------------------------------------------------------
export function setup() {
  http.post(`${BASE_URL}/auth/register`, {
    username: USERNAME,
    email: EMAIL,
    password: PASSWORD,
  });

  // Login to create a test post
  http.post(`${BASE_URL}/auth/login`, { email: EMAIL, password: PASSWORD });

  const postRes = http.post(`${BASE_URL}/posts`, {
    title: 'K6 Load Test Post',
    content: 'This post was created for load testing. It will be read and commented on.',
  }, { redirects: 0 });

  const postUrl = postRes.headers['Location'] || '/posts/1';
  const postId = postUrl.split('/').pop();

  http.get(`${BASE_URL}/auth/logout`);

  return { postUrl, postId };
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function login() {
  const res = http.post(`${BASE_URL}/auth/login`, {
    email: EMAIL,
    password: PASSWORD,
  }, { redirects: 0 });

  check(res, { 'login: redirect 303': (r) => r.status === 303 });
}

function logout() {
  const res = http.get(`${BASE_URL}/auth/logout`, { redirects: 0 });
  check(res, { 'logout: redirect 303': (r) => r.status === 303 });
  // Clear cookie jar to ensure clean state for next iteration
  http.cookieJar().clear(BASE_URL);
}

// ---------------------------------------------------------------------------
// Scenario 1 (2 VUs): login → view post → logout
// ---------------------------------------------------------------------------
export function viewPost(data) {
  group('Сценарій 1: Перегляд поста', function () {
    login();
    sleep(1);

    const res = http.get(`${BASE_URL}${data.postUrl}`);
    check(res, {
      'post page: status 200': (r) => r.status === 200,
      'post page: has title':  (r) => r.body.includes('K6 Load Test Post'),
    });
    sleep(1);

    logout();
  });
  sleep(1);
}

// ---------------------------------------------------------------------------
// Scenario 2 (1 VU): login → view post → home → view post → comment → logout
// ---------------------------------------------------------------------------
export function commentOnPost(data) {
  group('Сценарій 2: Коментар до поста', function () {
    login();
    sleep(1);

    const postPage = http.get(`${BASE_URL}${data.postUrl}`);
    check(postPage, { 'post page: status 200': (r) => r.status === 200 });
    sleep(1);

    const listPage = http.get(`${BASE_URL}/posts`);
    check(listPage, { 'posts list: status 200': (r) => r.status === 200 });
    sleep(1);

    http.get(`${BASE_URL}${data.postUrl}`);
    sleep(1);

    const commentRes = http.post(
      `${BASE_URL}/posts/${data.postId}/comments`,
      { content: 'K6 automated comment' },
      { redirects: 0 }
    );
    check(commentRes, { 'comment: redirect 303': (r) => r.status === 303 });
    sleep(1);

    logout();
  });
  sleep(1);
}

// ---------------------------------------------------------------------------
// Scenario 3 (1 VU): login → create post → logout
// ---------------------------------------------------------------------------
export function createPost() {
  group('Сценарій 3: Створення поста', function () {
    login();
    sleep(1);

    const formPage = http.get(`${BASE_URL}/posts/new`);
    check(formPage, { 'new post form: status 200': (r) => r.status === 200 });
    sleep(1);

    const createRes = http.post(`${BASE_URL}/posts`, {
      title: `K6 Post ${Date.now()}`,
      content: 'Post created during k6 load test.',
    }, { redirects: 0 });
    check(createRes, { 'create post: redirect 303': (r) => r.status === 303 });
    sleep(1);

    logout();
  });
  sleep(1);
}

// ---------------------------------------------------------------------------
// Scenario 4 (1 VU): login → view profile → edit profile → logout
// ---------------------------------------------------------------------------
export function editProfile() {
  group('Сценарій 4: Редагування профайлу', function () {
    login();
    sleep(1);

    const profilePage = http.get(`${BASE_URL}/profile/${USERNAME}`);
    check(profilePage, {
      'profile page: status 200': (r) => r.status === 200,
      'profile page: has username': (r) => r.body.includes(USERNAME),
    });
    sleep(1);

    const editPage = http.get(`${BASE_URL}/profile/edit`);
    check(editPage, { 'edit profile form: status 200': (r) => r.status === 200 });
    sleep(1);

    const updateRes = http.post(`${BASE_URL}/profile/edit`, {
      bio: `Updated by k6 at ${Date.now()}`,
    }, { redirects: 0 });
    check(updateRes, { 'update profile: redirect 303': (r) => r.status === 303 });
    sleep(1);

    logout();
  });
  sleep(1);
}
