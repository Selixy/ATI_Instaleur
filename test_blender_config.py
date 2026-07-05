from app.core.YamlLoader import get_yaml_loader

loader = get_yaml_loader()
app = loader.get_application_by_name('Blender')

if app:
    print(f'App: {app.name}')
    print(f'Has versions: {app.has_versions}')
    print(f'Default version index: {app.default_version_index}')
    print(f'Custom install path: {app.custom_install_path}')

    default_ver = app.get_default_version()
    if default_ver:
        print(f'\nDefault version: {default_ver.name}')
        print(f'Methods in default version: {len(default_ver.methods)}')

        if default_ver.methods:
            for i, method in enumerate(default_ver.methods):
                print(f'\nMethod {i+1}:')
                print(f'  Type: {method.type}')
                print(f'  URL: {method.url}')
                print(f'  Priority: {method.priority}')
                print(f'  Extra args: {method.extra_args}')
    else:
        print('No default version found!')
else:
    print('App Blender not found!')
