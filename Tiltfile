load('ext://uibutton', 'cmd_button', 'bool_input', 'location')
load('ext://namespace', 'namespace_create', 'namespace_inject')
namespace_create('oidc2fer')

docker_build(
    'localhost:5001/oidc2fer:latest',
    context='.',
    dockerfile='./Dockerfile',
    target = 'development',
    live_update=[
        sync('./src', '/app/src'),
        sync('./satosa', '/app/satosa'),
        sync('./tests', '/app/tests'),
    ]
)

docker_build(
    'localhost:5001/oidc-test-client:latest',
    context='docker/oidc-test-client'
)

watch_file('src/helm')

k8s_yaml(local('cd src/helm && helmfile -n oidc2fer -e dev template .'))
