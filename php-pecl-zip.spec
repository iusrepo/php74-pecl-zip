# Fedora spec file for php-pecl-zip
#
# Copyright (c) 2013-2016 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/4.0/
#
# Please, preserve the changelog entries
#
%global pecl_name zip
%global ini_name  40-%{pecl_name}.ini

Summary:      A ZIP archive management extension
Summary(fr):  Une extension de gestion des ZIP
Name:         php-pecl-zip
Version:      1.13.5
Release:      1%{?dist}
License:      PHP
Group:        Development/Languages
URL:          http://pecl.php.net/package/zip

Source:       http://pecl.php.net/get/%{pecl_name}-%{version}.tgz

BuildRequires: php-devel
BuildRequires: pkgconfig(libzip) >= 1.0.0
BuildRequires: zlib-devel
BuildRequires: php-pear

Requires:     php(zend-abi) = %{php_zend_api}
Requires:     php(api) = %{php_core_api}

Provides:     php-pecl(%{pecl_name}) = %{version}
Provides:     php-pecl(%{pecl_name})%{?_isa} = %{version}
Provides:     php-%{pecl_name} = %{version}-%{release}
Provides:     php-%{pecl_name}%{?_isa} = %{version}-%{release}


%description
Zip is an extension to create and read zip files.

%description -l fr
Zip est une extension pour créer et lire les archives au format ZIP.


%prep 
%setup -c -q

# Don't install/register tests
sed -e 's/role="test"/role="src"/' \
    -e '/LICENSE/s/role="doc"/role="src"/' \
    -i package.xml

cd %{pecl_name}-%{version}

# Sanity check, really often broken
extver=$(sed -n '/#define PHP_ZIP_VERSION/{s/.* "//;s/".*$//;p}' php5/php_zip.h)
if test "x${extver}" != "x%{version}%{?prever}"; then
   : Error: Upstream extension version is ${extver}, expecting %{version}%{?prever}.
   exit 1
fi

sed -e '/LICENSE_libzip/d' -i ../package.xml
# delete bundled libzip to ensure it is not used
rm -r lib

cd ..
: Create the configuration file
cat >%{ini_name} << 'EOF'
; Enable ZIP extension module
extension=%{pecl_name}.so
EOF

: Duplicate sources tree for ZTS build
cp -pr %{pecl_name}-%{version} %{pecl_name}-zts


%build
cd %{pecl_name}-%{version}
%{_bindir}/phpize
%configure \
  --with-libzip \
  --with-libdir=%{_lib} \
  --with-php-config=%{_bindir}/php-config

make %{?_smp_mflags}

cd ../%{pecl_name}-zts
%{_bindir}/zts-phpize
%configure \
  --with-libzip \
  --with-libdir=%{_lib} \
  --with-php-config=%{_bindir}/zts-php-config

make %{?_smp_mflags}


%install
make -C %{pecl_name}-%{version} install INSTALL_ROOT=%{buildroot}
install -D -m 644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}

# Install XML package description
install -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml

make -C %{pecl_name}-zts install INSTALL_ROOT=%{buildroot}
install -D -m 644 %{ini_name} %{buildroot}%{php_ztsinidir}/%{ini_name}

# Documentation
cd %{pecl_name}-%{version}
for i in $(grep 'role="doc"' ../package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 $i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done


%check
cd %{pecl_name}-%{version}
: minimal load test of NTS extension
%{_bindir}/php --no-php-ini \
    --define extension_dir=modules \
    --define extension=%{pecl_name}.so \
    --modules | grep %{pecl_name}

: upstream test suite for NTS extension
TEST_PHP_ARGS="-n -d extension_dir=$PWD/modules -d extension=%{pecl_name}.so" \
REPORT_EXIT_STATUS=1 \
NO_INTERACTION=1 \
TEST_PHP_EXECUTABLE=%{_bindir}/php \
%{_bindir}/php -n run-tests.php

cd ../%{pecl_name}-zts
: minimal load test of ZTS extension
%{_bindir}/zts-php --no-php-ini \
    --define extension_dir=modules \
    --define extension=%{pecl_name}.so \
    --modules | grep %{pecl_name}

: upstream test suite for ZTS extension
TEST_PHP_ARGS="-n -d extension_dir=$PWD/modules -d extension=%{pecl_name}.so" \
REPORT_EXIT_STATUS=1 \
NO_INTERACTION=1 \
TEST_PHP_EXECUTABLE=%{_bindir}/zts-php \
%{_bindir}/zts-php -n run-tests.php


%files
%license %{pecl_name}-%{version}/LICENSE
%doc %{pecl_docdir}/%{pecl_name}
%{pecl_xmldir}/%{name}.xml

%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{pecl_name}.so

%config(noreplace) %{php_ztsinidir}/%{ini_name}
%{php_ztsextdir}/%{pecl_name}.so


%changelog
* Fri Oct 14 2016 Remi Collet <remi@fedoraproject.org> - 1.13.5-1
- Update to 1.13.5

* Thu Jul 21 2016 Remi Collet <remi@fedoraproject.org> - 1.13.4-1
- Update to 1.13.4

* Mon Jun 27 2016 Remi Collet <remi@fedoraproject.org> - 1.13.3-2
- rebuild for https://fedoraproject.org/wiki/Changes/php70

* Thu Jun 23 2016 Remi Collet <remi@fedoraproject.org> - 1.13.3-1
- Update to 1.13.3

* Tue Mar  1 2016 Remi Collet <remi@fedoraproject.org> - 1.13.2-1
- Update to 1.13.2
- fix license management

* Wed Feb 10 2016 Remi Collet <remi@fedoraproject.org> - 1.13.1-3
- drop scriptlets (replaced file triggers in php-pear)
- ignore 1 test (change in php, FTBFS detected by Koschei)

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.13.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Sep 10 2015 Remi Collet <remi@fedoraproject.org> - 1.13.1-1
- Update to 1.13.1 (no change)

* Mon Sep  7 2015 Remi Collet <remi@fedoraproject.org> - 1.13.0-1
- Update to 1.13.0
- raise dependency on libzip 1.0.0
- don't install/register tests

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.12.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed May 06 2015 Remi Collet <remi@fedoraproject.org> - 1.12.5-2
- rebuild for new libzip

* Thu Apr 16 2015 Remi Collet <remi@fedoraproject.org> - 1.12.5-1
- Update to 1.12.5 (stable)

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.12.4-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Jun 19 2014 Remi Collet <rcollet@redhat.com> - 1.12.4-4
- rebuild for https://fedoraproject.org/wiki/Changes/Php56

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.12.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Apr 24 2014 Remi Collet <rcollet@redhat.com> - 1.12.4-2
- add numerical prefix to extension configuration file

* Wed Jan 29 2014 Remi Collet <remi@fedoraproject.org> - 1.12.4-1
- Update to 1.12.4 (stable) for libzip 0.11.2

* Thu Dec 12 2013 Remi Collet <remi@fedoraproject.org> - 1.12.3-1
- Update to 1.12.3 (stable)
- drop merged patch

* Thu Oct 24 2013 Remi Collet <remi@fedoraproject.org> 1.12.2-2
- upstream patch, don't use any libzip private struct
- drop LICENSE_libzip when system version is used
- always build ZTS extension

* Wed Oct 23 2013 Remi Collet <remi@fedoraproject.org> 1.12.2-1
- update to 1.12.2 (beta)
- drop merged patches
- install doc in pecl doc_dir
- install tests in pecl test_dir

* Thu Aug 22 2013 Remi Collet <rcollet@redhat.com> 1.12.1-5
- really really fix all spurious-executable-perm

* Thu Aug 22 2013 Remi Collet <rcollet@redhat.com> 1.12.1-4
- really fix all spurious-executable-perm

* Thu Aug 22 2013 Remi Collet <rcollet@redhat.com> 1.12.1-3
- fixes from review comments #999313: clarify License
- drop execution right from sources
- BR libzip-devel always needed

* Tue Aug 20 2013 Remi Collet <rcollet@redhat.com> 1.12.1-2
- refresh our merged patches from upstream git

* Thu Aug 08 2013 Remi Collet <rcollet@redhat.com> 1.12.1-1
- New spec for version 1.12.1 (beta)
