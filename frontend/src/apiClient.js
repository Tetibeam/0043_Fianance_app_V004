import axios from 'axios';

// 永続的なキャッシュストア
// key: URL, value: { etag: string, data: any }
const cacheStore = new Map();

const apiClient = axios.create({
  baseURL: '/api', // 必要に応じてベースURLを設定
});

// 1. リクエストインターセプター: If-None-Match ヘッダーの追加
apiClient.interceptors.request.use(config => {
  const url = config.url;
  const cachedEntry = cacheStore.get(url);

  if (cachedEntry && cachedEntry.etag) {
    config.headers['If-None-Match'] = cachedEntry.etag;
  }
  return config;
});

// レスポンスインターセプター: ETagの保存と 304 の処理を修正
// レスポンスインターセプター: ETagの保存と 304 の処理
apiClient.interceptors.response.use(
  response => {
    // 200 OK の場合
    const url = response.config.url;
    const etag = response.headers['etag'];

    // ETagとデータを両方保存
    if (etag) {
      // 🚨 修正点 3: cacheStore に ETag と data をセット
      cacheStore.set(url, { etag, data: response.data });
    }
    return response;
  },
  error => {
    // 304 Not Modified の処理
    if (error.response && error.response.status === 304) {
      const url = error.config.url;
      const cachedEntry = cacheStore.get(url);

      if (cachedEntry) {
        // 304の場合、キャッシュされたデータを注入して解決
        return Promise.resolve({
            status: 304,
            // 🚨 修正点 4: キャッシュされたデータを注入
            data: cachedEntry.data, 
            headers: error.response.headers,
            config: error.config
        });
      }
      // キャッシュがない場合 (初回304は通常ありえない)
      return Promise.reject(new Error(`304 received but no data cached for ${url}`));
    }
    return Promise.reject(error);
  }
);

export default apiClient;