load('ext://uibutton', 'cmd_button', 'bool_input', 'location')
load('ext://namespace', 'namespace_create', 'namespace_inject')
namespace_create('oidc2fer')

docker_build(
    'localhost:5001/oidc2fer:latest',
    context='.',
    dockerfile='./Dockerfile',
    only=['./src/satosa', './docker'],
    target = 'development',
    live_update=[
        sync('./src/satosa', '/app'),
    ]
)

k8s_yaml(local('cd src/helm && helmfile -n oidc2fer -e dev template .'))
