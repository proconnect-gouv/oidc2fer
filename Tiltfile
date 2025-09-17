load('ext://uibutton', 'cmd_button', 'bool_input', 'location')
load('ext://namespace', 'namespace_create', 'namespace_inject')
namespace_create('oidc2fer')

docker_build(
    'localhost:5001/oidc2fer:latest',
    context='.',
    dockerfile='./Dockerfile',
    only=['./src/satosa', './docker', './env.d'],
    target = 'development',
    live_update=[
        sync('./src/satosa', '/app'),
    ]
)

watch_file('src/helm')

k8s_yaml(local('cd src/helm && helmfile -n oidc2fer -e %s template .' % os.getenv('TILT_ENV', 'dev')))
