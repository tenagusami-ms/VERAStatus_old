setup(
    name='vlbi',
    version='0.0.1',
    description='package to access datain VLBI system',
    author='KAN-YA Yukitoshi',
    packages=find_packages(exclude=('tests', 'docs'), requires=['paramiko','kivy'])
)
