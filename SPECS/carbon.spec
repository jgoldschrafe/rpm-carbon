Summary:    Backend data caching and persistence daemon for Graphite
Name:       carbon
Version:    0.9.9
Release:    4%{?dist}
Source0:    %{name}-%{version}.tar.gz
Source1:    carbon-cache.init
Source2:    carbon-relay.init
Source3:    carbon-aggregator.init
Patch0:     %{name}-0.9.9-fhs-compliance.patch
License:    Apache Software License 2.0
Group:      Development/Libraries
Prefix:     %{_prefix}
BuildArch:  noarch
URL:        https://launchpad.net/graphite
Requires:   python-twisted
Requires:   python-txamqp
Requires:   python-zope-interface
Obsoletes:  python-carbon

%description
UNKNOWN

%prep
%setup -n %{name}-%{version}
%patch0 -p1

%build
%{__python} setup.py build

%install
%{__python} setup.py install --root=%{buildroot}

install -d -m 0755 %{buildroot}%{_sysconfdir}
install -d -m 0755 %{buildroot}%{_initrddir}
install -d -m 0755 %{buildroot}%{_localstatedir}/log/graphite/carbon-aggregator
install -d -m 0755 %{buildroot}%{_localstatedir}/log/graphite/carbon-cache
install -d -m 0755 %{buildroot}%{_localstatedir}/log/graphite/carbon-relay
install -d -m 0755 %{buildroot}%{_localstatedir}/run/graphite

mv %{buildroot}%{_prefix}/conf %{buildroot}%{_sysconfdir}/graphite
install -m 0755 %{SOURCE1} %{buildroot}%{_initrddir}/carbon-cache
install -m 0755 %{SOURCE2} %{buildroot}%{_initrddir}/carbon-relay
install -m 0755 %{SOURCE3} %{buildroot}%{_initrddir}/carbon-aggregator

find %{buildroot} -type f -name \*~\* -exec rm {} +

%clean
rm -rf %{buildroot}

%pre
getent group graphite >/dev/null || groupadd -r graphite
getent passwd graphite >/dev/null || \
    useradd -r -g graphite -d '/etc/graphite' -s /sbin/nologin \
    -c "Graphite Service User" uwsgi

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
%dir %attr(0755,graphite,graphite) %{_sysconfdir}/graphite
%{_initrddir}/carbon-aggregator
%{_initrddir}/carbon-cache
%{_initrddir}/carbon-relay
%{_sysconfdir}/graphite/*.example
%{_prefix}/bin/carbon-aggregator.py
%{_prefix}/bin/carbon-cache.py
%{_prefix}/bin/carbon-client.py
%{_prefix}/bin/carbon-relay.py
%{_prefix}/bin/validate-storage-schemas.py
%{python_sitelib}/%{name}-%{version}-py%{pyver}.egg-info
%{python_sitelib}/%{name}/*.py
%{python_sitelib}/%{name}/*.pyc
%{python_sitelib}/%{name}/*.pyo
%{python_sitelib}/%{name}/amqp0-8.xml
%{python_sitelib}/%{name}/aggregator/*.py
%{python_sitelib}/%{name}/aggregator/*.pyc
%{python_sitelib}/%{name}/aggregator/*.pyo
%attr(0755,graphite,graphite) %{_localstatedir}/log/graphite
%attr(0755,graphite,graphite) %{_localstatedir}/log/graphite/carbon-aggregator
%attr(0755,graphite,graphite) %{_localstatedir}/log/graphite/carbon-cache
%attr(0755,graphite,graphite) %{_localstatedir}/log/graphite/carbon-relay
%attr(0755,graphite,graphite) %{_localstatedir}/run/graphite

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
* Mon Nov  7 2011 Jeff Goldschrafe <jeff@holyhandgrenade.org> - 0.9.9-4
- Make init scripts run daemons as graphite user
- Fix logging options in init script

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
