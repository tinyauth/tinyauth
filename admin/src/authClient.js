// in src/authClient.js
import { AUTH_CHECK, AUTH_ERROR, AUTH_LOGOUT } from 'admin-on-rest';
import Cookies from 'universal-cookie';

const cookies = new Cookies();

export default (type, params) => {
    if (type === AUTH_LOGOUT) {
        window.location = '/logout';
        return Promise.resolve();
    }

    if (type === AUTH_ERROR) {
        const { status } = params;
        if (status === 401 || status === 403) {
            window.location = '/logout';
            return Promise.reject();
        }
        return Promise.resolve();
    }

    if (type === AUTH_CHECK) {
      cookies.get('tinycsrf') ? Promise.resolve() : Promise.reject();
    }

    return Promise.resolve('Unknown method');
}
