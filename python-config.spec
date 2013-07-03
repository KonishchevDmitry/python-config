%define module_name python_config
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}

# Run tests
%global with_check 1

Name:    python-config
Version: 0.1
Release: 1%{?dist}
Summary: A simple module for reading Python configuration files

Group:   Development/Libraries
License: GPLv3
URL:     https://github.com/KonishchevDmitry/python-config
Source:  http://pypi.python.org/packages/source/p/python-config/python-config-%version.tar.gz

Requires: python

BuildArch:     noarch
BuildRequires: make, python-setuptools
%if 0%{?with_check}
BuildRequires: pytest >= 2.2.4
%endif

%description
Python configuration files themselves are actual Python files. The module
reads only values in uppercase from them, checks that they contain only basic
Python types and returns a dictionary which corresponds to the configuration
file.


%prep
%setup -n %name-%version -q


%build
make PYTHON=%__python


%if 0%{?with_check}
%check
make PYTHON=%__python check
%endif


%install
[ "%buildroot" = "/" ] || rm -rf "%buildroot"

make PYTHON=%__python INSTALL_FLAGS="-O1 --root '%buildroot'" install


%files
%defattr(-,root,root,-)

%python_sitelib/%module_name.py
%python_sitelib/%module_name-*.egg-info


%clean
[ "%buildroot" = "/" ] || rm -rf "%buildroot"


%changelog
* Wed Jul 03 2013 Dmitry Konishchev <konishchev@gmail.com> - 0.1-1
- New package.
