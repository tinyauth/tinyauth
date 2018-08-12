import datetime
import json

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID
from fido2 import cbor, cose
from fido2.ctap2 import args
from fido2.utils import sha256

from tinyauth.models import WebAuthnCredential, db

from . import base


class TestCase(base.TestCase):

    def test_add_webauthn_credential(self):
        # We need a fake key to do the crypto
        be = default_backend()
        sk = ec.generate_private_key(ec.SECP256R1(), be)

        subject = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, 'fido2'),
        ])
        cert = x509.CertificateBuilder().\
            subject_name(subject).\
            issuer_name(subject).\
            public_key(sk.public_key()).\
            serial_number(x509.random_serial_number()).\
            not_valid_before(datetime.datetime.utcnow()).\
            not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=10)).\
            sign(sk, hashes.SHA256(), be)

        pk = cose.ES256.from_cryptography_key(sk.public_key())

        response = self.req('get', '/api/v1/users/charles/webauthn-credentials')
        assert response.status_code == 200
        assert json.loads(response.get_data(as_text=True)) == []

        response = self.req('post', '/api/v1/users/charles/webauthn-credentials')
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))

        data['challenge']

        '''
        At this point data will contain data that can mostly be fed directly to navigator.credentials.create:

        {
            'attestation': 'direct',
            'challenge': 'XXXXXXXXXXX',
            'excludeCredentials': [],
            'pubKeyCredParams': [{'alg': -7, 'type': 'public-key'}],
            'rp': {'id': 'localhost', 'name': 'Tinyauth'},
            'timeout': 60000,
            'user': {'displayName': 'charles', 'id': 'charles', 'name': 'charles'}
        }
        '''

        client_data = json.dumps({
            'challenge': 'WFhYWFhYWFhYWFg',
            'clientExtensions': {},
            'hashAlgorithm': 'SHA-256',
            'origin': 'https://localhost',
            'type': 'webauthn.create'
        }).encode('utf-8')

        import struct

        # Fake Attested Credential Data
        aaguid = b'\x00' * 16
        credential_id = b'dfdfdfdfdf'
        attested_cred_data = aaguid + struct.pack('>H', len(credential_id)) + credential_id + cbor.dumps(pk)

        # Fake Authenticator Data
        rp_id_hash = bytes(bytearray.fromhex('49960de5880e8c687434170f6476605b8fe4aeb9a28632c7995cf3ba831d9763'))
        extensions = b''
        auth_data = rp_id_hash + struct.pack('>BI', 0x41, 0) + attested_cred_data + extensions

        m = b'\0' + rp_id_hash + sha256(client_data) + credential_id + b'\x04' + pk[-2] + pk[-3]

        statement = {
            'x5c': [cert.public_bytes(serialization.Encoding.DER)],
            'sig': sk.sign(m, ec.ECDSA(hashes.SHA256())),
        }

        response = self.req('post', '/api/v1/users/charles/webauthn-credentials/complete', body={
            'name': 'asdasdasdasdasd',
            'publickey': {
                'clientData': list(bytearray(client_data)),
                'attObj': list(bytearray(cbor.dumps(args(
                        'fido-u2f',
                        auth_data,
                        statement,
                )))),
            },
        })

        assert response.status_code == 200
        completion = json.loads(response.get_data(as_text=True))

        assert completion == {
            'credential_id': 'ZGZkZmRmZGZkZg==',
            'id': '1',
            'name': 'asdasdasdasdasd',
            'sign_count': 0,
        }

    def test_list_user_credentials(self):
        db.session.add(WebAuthnCredential(
            user=self.user,
            name='yubikey-1',
            credential_id='zzzzzz',
            sign_count=0,
        ))
        db.session.commit()

        response = self.req('get', '/api/v1/users/charles/webauthn-credentials')

        assert response.status_code == 200
        assert json.loads(response.get_data(as_text=True)) == [{
            'id': '1',
            'name': 'yubikey-1',
            'sign_count': 0,
            'credential_id': 'zzzzzz',
        }]

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'ListWebAuthCredentials'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 200,
            'request.username': 'charles',
        }

    def test_get_user_credential(self):
        db.session.add(WebAuthnCredential(
            user=self.user,
            name='yubikey-1',
            credential_id='zzzzzz',
            sign_count=0,
        ))
        db.session.commit()

        response = self.req('get', '/api/v1/users/charles/webauthn-credentials/1')

        assert response.status_code == 200
        assert json.loads(response.get_data(as_text=True)) == {
            'id': '1',
            'name': 'yubikey-1',
            'sign_count': 0,
            'credential_id': 'zzzzzz',
        }

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'GetWebAuthnCredential'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 200,
            'request.username': 'charles',
            'request.credential': '1',
        }

    def test_delete_user_credential(self):
        db.session.add(WebAuthnCredential(
            user=self.user,
            name='yubikey-1',
            credential_id='zzzzzz',
            sign_count=0,
        ))
        db.session.commit()

        response = self.req('delete', '/api/v1/users/charles/webauthn-credentials/1')

        assert response.status_code == 201
        assert json.loads(response.get_data(as_text=True)) == {}

        response = self.req('get', '/api/v1/users/charles/webauthn-credentials')
        assert len(json.loads(response.get_data(as_text=True))) == 0

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'DeleteWebAuthnCredential'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 201,
            'request.username': 'charles',
            'request.credential': '1',
        }
