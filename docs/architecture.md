# Principe de fonctionnement de la passerelle ProConnect vers RENATER (`OIDC2FER`)

## Vue d'ensemble

Ce premier schéma donne un aperçu des échanges entre :
* un Fournisseur de Service ProConnecté (ex. https://pad.numerique.gouv.fr) ;
* le service ProConnect (hébergé sur `https://auth.agentconnect.gouv.fr`) ;
* la passerelle `OIDC2FER` (hébergé sur `https://renater.agentconnect.gouv.fr`) ;
* le service de _discovery_ ou _Where Are You From (WAYF)_ RENATER qui permet à l'utilisateur de choisir son établissement de rattachement, hébergé sur https://discovery.renater.fr/agentconnect/ ;
* le serveur d'identité SAML de l'établissement sélectionné (par exemple, https://cas.inria.fr).

``` mermaid
sequenceDiagram
    participant FS as Fournisseur<br>de Service
    participant ProConnect
    box LightYellow
        participant OIDC2FER
    end
    participant WAYF as WAYF<br>RENATER
    participant IdP as IdP SAML

    FS->>ProConnect: OIDC auth request
    ProConnect->>OIDC2FER: OIDC auth request
    OIDC2FER->>WAYF: discovery request
    WAYF->>OIDC2FER: IdP entityID
    OIDC2FER->>IdP: SAML AuthnRequest
    IdP->>OIDC2FER: SAML Assertion
    OIDC2FER->>ProConnect: OIDC tokens+userinfo
    ProConnect->>FS: OIDC tokens+userinfo
```

## Détail des échanges

Noter que le schéma précédent ne reflète pas le détail des échanges entre l'utilisateur, son navigateur (qu'il est utile de distinguer pour illustrer que plusieurs échanges se font sans intervention humaine), et les différents services mentionnés. En voici une version exhaustive :

``` mermaid
sequenceDiagram
    actor Utilisateur
    participant Navigateur
    participant FS as Fournisseur<br>de Service
    participant ProConnect
    box LightYellow
        participant OIDC2FER
    end
    participant WAYF as WAYF<br>RENATER
    participant IdP SAML
    
    Utilisateur->>Navigateur: Saisie/clic URL FS
    Navigateur->>FS: Requête d'une page du FS
    opt si pas de session FS ouverte
        FS->>Utilisateur: Présentation page d'accueil avec bouton ProConnect
        Utilisateur->>FS: Clic bouton ProConnect
        FS->>Navigateur: Redirection OIDC vers ProConnect avec state, nonce
        Navigateur->>ProConnect: Requête GET avec state, nonce
        opt si pas de session ProConnect ouverte
            ProConnect->>Utilisateur: Présentation mire ProConnect
            Utilisateur->>ProConnect: Clic bouton RENATER, ou saisie "robert@univ-exemple.fr"
            ProConnect->>Navigateur: Redirection OIDC vers OIDC2FER avec state, nonce
            Navigateur->>OIDC2FER: Requête GET avec state, nonce
            OIDC2FER->>Navigateur: Redirection vers WAYF
            Navigateur->>WAYF: Requête GET
            opt si pas de préselection enregistrée dans le WAYF
                WAYF->>Utilisateur: Présentation liste d'établissements autorisés
                Utilisateur->>WAYF: Choix d'un établissement
            end
            WAYF->>Navigateur: Redirection vers OIDC2FER avec entityID IdP
            Navigateur->>OIDC2FER: Requête GET avec entityID IdP
            OIDC2FER->>Navigateur: Redirection vers IdP avec AuthnRequest SAML dans l'URL
            Navigateur->>IdP SAML: Requête GET avec AuthnRequest SAML dans l'URL
            opt si pas de session IdP ouverte
                IdP SAML->>Utilisateur: Présentation mire de connexion IdP
                Utilisateur->>IdP SAML: Saisie identifiants de connexion
            end
            IdP SAML->>Navigateur: Page avec formulaire contenant assertion SAML
            Navigateur->>OIDC2FER: Requête POST avec assertion SAML
            Note over OIDC2FER: Validation<br>eduPersonAffiliation
            Note over OIDC2FER: Conversion attributs<br>SAML vers OIDC
            OIDC2FER->>Navigateur: Redirection vers callback OIDC ProConnect avec authorization_code
            Navigateur->>ProConnect: Requête GET avec authorization_code
            ProConnect->>OIDC2FER: Demande tokens avec authorization_code
            OIDC2FER->>ProConnect: Tokens OIDC
            ProConnect->>OIDC2FER: Demande userinfo avec accessToken
            OIDC2FER->>ProConnect: userinfo
        end
        ProConnect->>Navigateur: Redirection vers callback OIDC FS avec authorization_code
        Navigateur->>FS: Requête GET avec authorization_code
        FS->>ProConnect: Demande tokens avec authorization_code
        ProConnect->>FS: Tokens OIDC
        FS->>ProConnect: Demande userinfo avec accessToken
        ProConnect->>FS: userinfo
    end
    FS->>Utilisateur: Contenu du service
```
