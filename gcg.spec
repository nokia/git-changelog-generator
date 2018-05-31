%define _name gcg
%define name python-gcg
%define release 1
# explicitly override this for the sake of rpmbuild on Ubuntu (dash shell)
%define _buildshell /bin/bash
# See https://fedoraproject.org/wiki/Packaging:Python
%define __python /usr/bin/python2
%define python2_sitelib     %(%{__python} -c "from distutils.sysconfig import get_python_lib; import sys; sys.stdout.write(get_python_lib())")

Summary: Git Changelog Generator
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{_name}-%{version}.tar.gz
License: BSD-3-Clause
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{_name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Waldek Maleska <waldek.maleska@nokia.com>
Requires: python2-semver >= 2.0.1, python-jinja2 >= 2.7, GitPython >= 1.0.1, python-setuptools >= 0.9.8
Url: https://github.com/nokia/git-changelog-generator

%description
GCG stands for Git Changelog Generator.

%prep
%setup -n %{_name}-%{version}

%build
%{__python} setup.py build

%install
%{__python} setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES --skip-build --install-lib %{python2_sitelib}

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
