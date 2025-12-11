import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 5,              // 5 virtual users
  duration: '30s',     // run for 30 seconds
};

const BASE_URL = 'http://ui-service:5006'; // ui-service inside Docker network

export default function () {
  // Hit home page
  let res = http.get(`${BASE_URL}/`);
  check(res, {
    'home page status is 200': (r) => r.status === 200,
  });

  // (Optional) Call product-service directly
  let products = http.get('http://product-service:5001/products');
  check(products, {
    'products status is 200': (r) => r.status === 200,
  });

  sleep(1);
}

