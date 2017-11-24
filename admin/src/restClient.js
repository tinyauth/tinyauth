import { simpleRestClient, fetchUtils } from 'admin-on-rest';
// import cookie from "react-cookie";

const httpClient = (url, options = {}) => {
    if (!options.headers) {
        options.headers = new Headers({ Accept: 'application/json' });
    }
    options['credentials'] = 'same-origin';

    // options.headers.set('X-CSRF-Token', cookie.load('tinycsrf'));
    options.headers.set('X-CSRF-Token', '99a1494b-9f33-49af-9a5e-a2b6a93a1a72');
    return fetchUtils.fetchJson(url, options);
}

export const request = (method, uri, body=null) => {
    let options = {method: method};
    if (body) {
        options['body'] = JSON.stringify(body);
    }
    return httpClient(window.API_ENDPOINT_URL + uri, options);
}

const restClient = simpleRestClient(window.API_ENDPOINT_URL, httpClient);
export default (type, resource, params) => new Promise(resolve => setTimeout(() => resolve(restClient(type, resource, params)), 500));
