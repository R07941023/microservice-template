import Keycloak from 'keycloak-js';

const keycloak = new Keycloak({
  url: 'https://keycloak.mydormroom.dpdns.org',
  realm: 'master',
  clientId: 'mydormroomapp',
});

export default keycloak;
