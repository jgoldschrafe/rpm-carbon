%if 0%{?rhel} < 6
%define python_sitelib  %(%{__python} -c "from distutils.sysconfig import get_python_lib; import sys; sys.stdout.write(get_python_lib())")
%define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; import sys; sys.stdout.write(get_python_lib(1))")
%define python_version  %(%{__python} -c "import sys; sys.stdout.write(sys.version[:3])")
%endif

Summary:    Backend data caching and persistence daemon for Graphite
Name:       carbon
Version:    0.9.10
Release:    1%{?dist}
Source0:    %{name}-%{version}.tar.gz
Source1:    carbon.conf.default
Source2:    carbon-cache.init
Source3:    carbon-relay.init
Source4:    carbon-aggregator.init
Source5:    carbon.logrotate
Patch0:     %{name}-0.9.10-fhs-compliance.patch
License:    Apache Software License 2.0
Group:      Development/Libraries
Prefix:     %{_prefix}
BuildArch:  noarch
URL:        https://launchpad.net/graphite
Requires:   logrotate
Requires:   python-twisted
Requires:   python-txamqp
Requires:   python-zope-interface
Obsoletes:  python-carbon


%description
Carbon is the backend storage application of the Graphite framework, providing
data collection, caching, and persistence services.


%prep
%setup
%patch0 -p1


%build
%{__python} setup.py build


%install
rm -rf %{buildroot}

%{__python} setup.py install --root=%{buildroot}

install -d -m 0755 %{buildroot}%{_sysconfdir}/logrotate.d
install -d -m 0755 %{buildroot}%{_initrddir}
install -d -m 0755 %{buildroot}%{_sharedstatedir}/carbon/rrd
install -d -m 0755 %{buildroot}%{_localstatedir}/log/carbon/carbon-cache-a
install -d -m 0755 %{buildroot}%{_localstatedir}/run/carbon

mv %{buildroot}%{_prefix}/conf %{buildroot}%{_sysconfdir}/carbon
install -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/carbon/carbon.conf
install -m 0755 %{SOURCE2} %{buildroot}%{_initrddir}/carbon-cache
install -m 0755 %{SOURCE3} %{buildroot}%{_initrddir}/carbon-relay
install -m 0755 %{SOURCE4} %{buildroot}%{_initrddir}/carbon-aggregator

# Install examples as configurations
cp -a %{buildroot}%{_sysconfdir}/carbon/{aggregation-rules.conf.example,aggregation-rules.conf}
cp -a %{buildroot}%{_sysconfdir}/carbon/{rewrite-rules.conf.example,rewrite-rules.conf}
cp -a %{buildroot}%{_sysconfdir}/carbon/{storage-aggregation.conf.example,storage-aggregation.conf}
cp -a %{buildroot}%{_sysconfdir}/carbon/{storage-schemas.conf.example,storage-schemas.conf}
install -m 0644 %{SOURCE5} %{buildroot}%{_sysconfdir}/logrotate.d/carbon


%clean
rm -rf %{buildroot}


%pre
getent group graphite >/dev/null || groupadd -r graphite
getent passwd graphite >/dev/null || \
    useradd -r -g graphite -d '/etc/graphite' -s /sbin/nologin \
    -c "Graphite Service User" graphite


%post
for svc in carbon-{aggregator,cache,relay}; do
    /sbin/chkconfig --add "$svc"
done


%preun
if [ $1 -eq 0 ]; then
    for svc in carbon-{aggregator,cache,relay}; do
        /sbin/service "$svc" stop >/dev/null 2>&1
        /sbin/chkconfig --del "$svc"
    done
fi


%postun
if [ $1 -ge 1 ]; then
    for svc in carbon-{aggregator,cache,relay}; do
        /sbin/service "$svc" condrestart >/dev/null 2>&1 || :
    done
fi


%files
%defattr(-,root,root)
%dir %{_sysconfdir}/carbon
%doc %{_sysconfdir}/carbon/*.example
%config(noreplace) %{_sysconfdir}/carbon/*.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/carbon
%{_initrddir}/carbon-aggregator
%{_initrddir}/carbon-cache
%{_initrddir}/carbon-relay
%{_bindir}/carbon-aggregator.py
%{_bindir}/carbon-cache.py
%{_bindir}/carbon-client.py
%{_bindir}/carbon-relay.py
%{_bindir}/validate-storage-schemas.py
%if 0%{?rhel} >= 6
%{python_sitelib}/%{name}-%{version}-py%{pyver}.egg-info
%endif
%{python_sitelib}/%{name}/*.py
%{python_sitelib}/%{name}/*.pyc
%{python_sitelib}/%{name}/*.pyo
%{python_sitelib}/%{name}/amqp0-8.xml
%{python_sitelib}/%{name}/aggregator/*.py
%{python_sitelib}/%{name}/aggregator/*.pyc
%{python_sitelib}/%{name}/aggregator/*.pyo
%attr(0755,graphite,graphite) %{_sharedstatedir}/carbon
%attr(0755,graphite,graphite) %{_localstatedir}/log/carbon
%attr(0755,graphite,graphite) %{_localstatedir}/run/carbon

# This is questionable and should probably be split into another package
%{python_sitelib}/twisted/plugins/carbon_aggregator_plugin.py
%{python_sitelib}/twisted/plugins/carbon_aggregator_plugin.pyc
%{python_sitelib}/twisted/plugins/carbon_aggregator_plugin.pyo
%{python_sitelib}/twisted/plugins/carbon_cache_plugin.py
%{python_sitelib}/twisted/plugins/carbon_cache_plugin.pyc
%{python_sitelib}/twisted/plugins/carbon_cache_plugin.pyo
%{python_sitelib}/twisted/plugins/carbon_relay_plugin.py
%{python_sitelib}/twisted/plugins/carbon_relay_plugin.pyc
%{python_sitelib}/twisted/plugins/carbon_relay_plugin.pyo

%changelog
* Tue Jul 10 2012 Jeff Goldschrafe <jeff@holyhandgrenade.org> - 0.9.10-1
- Update to version 0.9.10
- Move /etc/graphite and /var/lib/graphite to preferred /etc/carbon and
  /var/lib/carbon directories respectively, as per FHS-style documentation in
  new carbon.conf
- Fix copy/paste boilerplate in init scripts
- Add logrotate.d fragment
- Minor fixes and improvements (thanks Gavin Carr)

* Fri Dec 16 2011 Jeff Goldschrafe <jeff@holyhandgrenade.org> - 0.9.9-4
- Fix copy/paste bug in user creation

* Sun Nov  6 2011 Jeff Goldschrafe <jeff@holyhandgrenade.org> - 0.9.9-3
- Rename python-carbon to carbon

* Fri Nov  4 2011 Jeff Goldschrafe <jeff@holyhandgrenade.org> - 0.9.9-2
- Add graphite user/group
- Add init scripts
- Add /var/run/graphite to store PIDs

* Wed Oct 26 2011 Jeff Goldschrafe <jeff@holyhandgrenade.org> - 0.9.9-1
- Bump to version 0.9.9

* Wed Oct 26 2011 Jeffrey Goldschrafe <jeff@holyhandgrenade.org> - 0.9.7-1
- Initial package for Fedora
