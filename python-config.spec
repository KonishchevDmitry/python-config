%if 0%{?fedora} > 12 || 0%{?epel} >= 6
%bcond_without python3
%else
%bcond_with python3
%endif

%if 0%{?epel} >= 7
%bcond_without python3_other
%endif

%if 0%{?rhel} <= 6
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%endif
%if 0%{with python3}
%{!?__python3: %global __python3 /usr/bin/python3}
%{!?python3_sitelib: %global python3_sitelib %(%{__python3} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python3_pkgversion: %global python3_pkgversion 3}
%endif  # with python3

%bcond_without tests

%global project_name pcore
%global project_description %{expand:
Python configuration files themselves are actual Python files. The module
reads only values in uppercase from them, checks that they contain only basic
Python types and returns a dictionary which corresponds to the configuration
file.

Note: if you want to validate the configuration values, take a look at
https://github.com/KonishchevDmitry/object-validator project.}

Name:    python-config
Version: 0.1.2
Release: 3%{?dist}
Summary: A simple module for reading Python configuration files

Group:   Development/Libraries
License: GPLv3
URL:     https://github.com/KonishchevDmitry/python-config
Source:  http://pypi.python.org/packages/source/p/python-config/python-config-%version.tar.gz

BuildArch:     noarch
BuildRequires: make
BuildRequires: python2-devel python-setuptools
%if 0%{with check}
BuildRequires: pytest >= 2.2.4
%endif  # with tests

%description %{project_description}


%if 0%{with python3}
%package -n python%{python3_pkgversion}-config
Summary: %{summary}
BuildRequires: python%{python3_pkgversion}-devel
BuildRequires: python%{python3_pkgversion}-setuptools
%if 0%{with check}
BuildRequires: python%{python3_pkgversion}-pytest >= 2.2.4
%endif  # with tests

%description -n python%{python3_pkgversion}-config %{project_description}
%endif  # with python3


%if 0%{with python3_other}
%package -n python%{python3_other_pkgversion}-config
Summary: %{summary}
BuildRequires: python%{python3_other_pkgversion}-devel
BuildRequires: python%{python3_other_pkgversion}-setuptools
%if 0%{with check}
BuildRequires: python%{python3_other_pkgversion}-pytest >= 2.2.4
%endif  # with tests

%description -n python%{python3_other_pkgversion}-config %{project_description}
%endif  # with python3_other


%prep
%setup -n %name-%version -q


%build
make PYTHON=%{__python2}
%if 0%{with python3}
make PYTHON=%{__python3}
%endif  # with python3
%if 0%{with python3_other}
make PYTHON=%{__python3_other}
%endif  # with python3_other


%check
%if 0%{with check}
make PYTHON=%{__python2} check
%if 0%{with python3}
make PYTHON=%{__python3} check
%endif  # with python3
%if 0%{with python3_other}
make PYTHON=%{__python3_other} check
%endif  # with python3_other
%endif  # with check


%install
[ "%buildroot" = "/" ] || rm -rf "%buildroot"

make PYTHON=%{__python2} INSTALL_FLAGS="-O1 --root '%buildroot'" install
%if 0%{with python3}
make PYTHON=%{__python3} INSTALL_FLAGS="-O1 --root '%buildroot'" install
%endif  # with python3
%if 0%{with python3_other}
make PYTHON=%{__python3_other} INSTALL_FLAGS="-O1 --root '%buildroot'" install
%endif  # with python3_other


%files
%defattr(-,root,root,-)
%{python2_sitelib}/python_config.py*
%{python2_sitelib}/python_config-%{version}-*.egg-info
%doc ChangeLog INSTALL README

%if 0%{with python3}
%files -n python%{python3_pkgversion}-config
%defattr(-,root,root,-)
%{python3_sitelib}/python_config.py
%{python3_sitelib}/__pycache__/python_config.*.py*
%{python3_sitelib}/python_config-%{version}-*.egg-info
%doc ChangeLog INSTALL README
%endif  # with python3

%if 0%{with python3_other}
%files -n python%{python3_other_pkgversion}-config
%defattr(-,root,root,-)
%{python3_other_sitelib}/python_config.py
%{python3_other_sitelib}/__pycache__/python_config.*.py*
%{python3_other_sitelib}/python_config-%{version}-*.egg-info
%doc ChangeLog INSTALL README
%endif  # with python3_other


%clean
[ "%buildroot" = "/" ] || rm -rf "%buildroot"


%changelog
* Sun Feb 10 2019 Mikhail Ushanov <gm.mephisto@gmail.com> - 0.1.2-3
- Enable tests for python36

* Sun Jan 13 2019 Mikhail Ushanov <gm.mephisto@gmail.com> - 0.1.2-2
- Add python3 package build for EPEL

* Mon Dec 12 2016 Dmitry Konishchev <konishchev@gmail.com> - 0.1.2-1
- New version.

* Wed Jul 03 2013 Dmitry Konishchev <konishchev@gmail.com> - 0.1.1-1
- New version.

* Wed Jul 03 2013 Dmitry Konishchev <konishchev@gmail.com> - 0.1-1
- New package.
