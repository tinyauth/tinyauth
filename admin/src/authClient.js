// in src/authClient.js
import { AUTH_CHECK, AUTH_ERROR, AUTH_LOGIN, AUTH_LOGOUT } from 'admin-on-rest';
// import cookie from 'react-cookie';


export default (type, params) => {
    // console.log(cookie.load('tinycsrf'));
    console.log(type);
    console.log(params);

    //if (type === AUTH_LOGOUT) {
    //    localStorage.removeItem('tinycsrf');
    //    return Promise.resolve();
    //}

    //if (type === AUTH_ERROR) {
    //    const { status } = params;
    //    if (status === 401 || status === 403) {
    //        localStorage.removeItem('tinycsrf');
    //        return Promise.reject();
    //    }
    //    return Promise.resolve();
    //}

    //if (type === AUTH_CHECK) {
    //  console.log(cookie.load('tinycsrf'));
    //    return Promise.resolve();
    //}

    return Promise.resolve();
}
