import os


def create_directories_from_filenames(a_dir, b_dir):
    filenames = os.listdir(a_dir)

    for filename in filenames:
        if filename.lower() == 'readme' or '.' not in filename:
            continue

        directory_name = os.path.splitext(filename)[0]

        new_directory_path = os.path.join(b_dir, directory_name)

        if not os.path.exists(new_directory_path):
            os.makedirs(new_directory_path)
            readme_file_path = os.path.join(new_directory_path, 'README.md')
            with open(readme_file_path, 'w') as readme_file:
                readme_file.write('README.md')
            print(f'Created directory: {new_directory_path}')
            print(f'Created and updated README file: {readme_file_path}')
        else:
            print(f'Directory already exists: {new_directory_path}')

    print('All directories and README files created successfully!')


a_directory = r'C:\a'
b_directory = r'C:\b'

create_directories_from_filenames(a_directory, b_directory)