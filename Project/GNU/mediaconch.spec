%define mediaconch_version          16.11
%define libmediainfo_version        0.7.91
%define libzen_version              0.4.34

%if 0%{?fedora} || 0%{?centos_version} >= 600 || 0%{?rhel_version} >= 600
%define libmediainfo_name libmediainfo
%define libzen_name libzen
%else
%define libmediainfo_name libmediainfo0
%define libzen_name libzen0
%endif

# CentOS also set rhel macro
%if ! 0%{?suse_version} && ! 0%{?rhel} || 0%{?suse_version} >= 1200 || 0%{?centos_version} >= 700
%define build_server 1
%else
%define build_server 0
%endif

%if ! 0%{?rhel} && ! 0%{?suse_version} || 0%{?suse_version} >= 1200
%define build_gui 1
%else
%define build_gui 0
%endif

Name:           mediaconch-policy
Version:        %{mediaconch_version}
Release:        1
Summary:        Policy checker for video and audio files (CLI)

Group:          Applications/Multimedia
License:        MPL-2.0+/GPL-3.0+
URL:            http://MediaArea.net/MediaConch
Packager:       MediaArea.net SARL <info@mediaarea.net>
Source0:        mediaconch_%{version}.tar.gz

Requires:       %{libzen_name}%{?_isa} >= %{libzen_version}
Requires:       %{libmediainfo_name}%{?_isa} >= %{libmediainfo_version}

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig
BuildRequires:  libmediainfo-devel >= %{libmediainfo_version}
BuildRequires:  libzen-devel >= %{libzen_version}
BuildRequires:  pkgconfig
BuildRequires:  zlib-devel
BuildRequires:  libtool
BuildRequires:  automake
BuildRequires:  autoconf
BuildRequires:  zlib-devel
BuildRequires:  libxml2-devel
BuildRequires:  libxslt-devel
BuildRequires:  sqlite-devel

%if ! 0%{?rhel} || 0%{?centos_version} >= 700
BuildRequires:  libevent-devel
%endif

%if 0%{?centos_version} < 600 || 0%{?rhel_version} < 600
BuildRequires:  curl-devel
%else
BuildRequires:  libcurl-devel
%endif

%if 0%{?fedora}
BuildRequires:  pkgconfig(systemd)
%endif

%if 0%{?suse_version}
%if 0%{?is_opensuse}
BuildRequires:  libjansson-devel
%endif
%else
%if ! 0%{?rhel} || 0%{?centos_version} >= 700
BuildRequires:  jansson-devel
%endif
%endif

%if 0%{?mageia}
BuildRequires:  sane-backends-iscan
BuildRequires:  libuuid-devel
%endif

# GUI dependencies
%if 0%{?build_gui}
%if 0%{?fedora}
BuildRequires:  pkgconfig(Qt5)
BuildRequires:  desktop-file-utils
%if 0%{?fedora} >= 24
BuildRequires:  pkgconfig(Qt5WebEngine)
%else
BuildRequires:  pkgconfig(Qt5WebKit)
%endif
%else
BuildRequires:  libqt4-devel
%endif

%if 0%{?suse_version}
BuildRequires:  libQtWebKit-devel
BuildRequires:  update-desktop-files
%endif

%if 0%{?mageia}
%ifarch x86_64
BuildRequires:  lib64qtwebkit2.2-devel
%else
BuildRequires:  libqtwebkit2.2-devel
%endif
%endif
%endif # GUI

%description
MediaConch-Policy is an policy checker, reporter,
and fixer that targets preservation-level audiovisual files
(specifically Matroska, Linear Pulse Code Modulation (LPCM)
and FF Video Codec 1 (FFV1)).

This project is maintained by MediaArea and funded by PREFORMA.

This package includes the command line interface.

%if 0%{?build_server}
%package server
Summary:    Policy checker for video and audio files (Server)
Group:      Applications/Multimedia
Requires:   %{libzen_name}%{?_isa} >= %{libzen_version}
Requires:   %{libmediainfo_name}%{?_isa} >= %{libmediainfo_version}
%if 0%{?fedora}
%{?systemd_requires}
%endif
%endif # Server

%if 0%{?build_gui}
%package gui
Summary:    Policy checker for video and audio files (GUI)
Group:      Applications/Multimedia
Requires:   %{libzen_name}%{?_isa} >= %{libzen_version}
Requires:   %{libmediainfo_name}%{?_isa} >= %{libmediainfo_version}

%description gui
MediaConch-Policy is an policy checker, reporter,
and fixer that targets preservation-level audiovisual files
(specifically Matroska, Linear Pulse Code Modulation (LPCM)
and FF Video Codec 1 (FFV1)).

This project is maintained by MediaArea and funded by PREFORMA.

This package includes the graphical user interface.
%endif # GUI

%if 0%{?build_server}
%description server
MediaConch-Policy-Server is an policy checker, policy checker, reporter,
and fixer that targets preservation-level audiovisual files
(specifically Matroska, Linear Pulse Code Modulation (LPCM)
and FF Video Codec 1 (FFV1)).

This project is maintained by MediaArea and funded by PREFORMA.

This package includes the server.
%endif # Server

%prep
%setup -q -n MediaConch
sed -i 's/.$//' *.txt *.html Release/*.txt

find Source -type f -exec chmod 644 {} ';'
chmod 644 *.html *.txt Release/*.txt

pushd Project/GNU/CLI
    autoreconf -i
popd

%if 0%{?build_server}
pushd Project/GNU/Server
    autoreconf -i
popd
%endif # Server

%if 0%{?build_gui}
pushd Project/Qt
    chmod u+x prepare
    %if 0%{?suse_version} && ! 0%{?is_opensuse}
        ./prepare NO_JANSSON=yes
    %else
        ./prepare
    %endif
popd
%endif # GUI

%build
export CFLAGS="%{optflags}"
export CXXFLAGS="%{optflags}"

# build CLI
pushd Project/GNU/CLI
    %if 0%{?suse_version} && ! 0%{?is_opensuse}
        %if 0%{?suse_version} < 1200
            %configure --without-jansson --without-libevent
        %else
            %configure --without-jansson
        %endif
    %else
        %if 0%{?suse_version} && 0%{?suse_version} < 1200
            %configure --without-libevent
        %else
        	%if ! 0%{?rhel} || 0%{?centos_version} >= 700
                %configure
            %else
                %if 0%{?rhel} == 5
                    %configure --without-jansson --without-libevent --without-sqlite
                %else
                    %configure --without-jansson --without-libevent
                %endif
            %endif
        %endif
    %endif
    make %{?_smp_mflags}
popd

# build server
%if 0%{?build_server}
pushd Project/GNU/Server
    %if 0%{?suse_version} && ! 0%{?is_opensuse}
        %configure --without-jansson
    %else
        %configure
    %endif
    make %{?_smp_mflags}
popd
%endif #Server

# now build GUI
%if 0%{?build_gui}
pushd Project/Qt
    make %{?_smp_mflags}
popd
%endif # GUI


%install
pushd Project/GNU/CLI
    make install DESTDIR=%{buildroot}
popd

%if 0%{?build_server}
pushd Project/GNU/Server
    make install DESTDIR=%{buildroot}
popd
%endif # Server

%if 0%{?build_gui}
pushd Project/Qt
    install -dm 755 %{buildroot}%{_bindir}
    install -m 755 mediaconch-policy-gui %{buildroot}%{_bindir}
popd

# directories
install -dm 755 %{buildroot}%{_datadir}/icons/hicolor/256x256/apps
install -dm 755 %{buildroot}%{_datadir}/pixmaps
install -dm 755 %{buildroot}%{_datadir}/applications
install -dm 755 %{buildroot}%{_datadir}/apps/konqueror/servicemenus
install -dm 755 %{buildroot}%{_datadir}/kde4/services/ServiceMenus/
install -dm 755 %{buildroot}%{_datadir}/appdata/

# files
install -m 644 Source/Resource/Image/MediaConch.png %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/mediaconch-policy.png
install -m 644 Source/Resource/Image/MediaConch.png %{buildroot}%{_datadir}/pixmaps/mediaconch-policy.png
install -m 644 Project/GNU/GUI/mediaconch-gui.desktop %{buildroot}%{_datadir}/applications/mediaconch-policy-gui.desktop
install -m 644 Project/GNU/GUI/mediaconch-gui.kde3.desktop %{buildroot}%{_datadir}/apps/konqueror/servicemenus/mediaconch-policy-gui.desktop
install -m 644 Project/GNU/GUI/mediaconch-gui.kde4.desktop %{buildroot}%{_datadir}/kde4/services/ServiceMenus/mediaconch-policy-gui.desktop
install -m 644 Project/GNU/GUI/mediaconch-gui.appdata.xml %{buildroot}%{_datadir}/appdata/mediaconch-policy-gui.appdata.xml

# menu-entry
%if 0%{?suse_version}
  %suse_update_desktop_file -n mediaconch-policy-gui AudioVideo AudioVideoEditing
  %suse_update_desktop_file -n %{buildroot}%{_datadir}/apps/konqueror/servicemenus/mediaconch-policy-gui.desktop AudioVideo AudioVideoEditing
  %suse_update_desktop_file -n %{buildroot}%{_datadir}/kde4/services/ServiceMenus/mediaconch-policy-gui.desktop AudioVideo AudioVideoEditing
%endif

%if 0%{?fedora}
install -dm 755 %{buildroot}%{_unitdir}
install -m 644 -p Project/GNU/Server/mediaconch-policyd.service  %{buildroot}%{_unitdir}/mediaconch-policyd.service
install -dm 755 %{buildroot}%{_sysconfdir}/%{name}
install -m 644 -p Project/GNU/Server/MediaConch.rc  %{buildroot}%{_sysconfdir}/%{name}/MediaConch.rc
%endif
%endif #GUI

%if 0%{?fedora}
%post server
%systemd_post mediaconch-policyd.service

%preun server
%systemd_preun mediaconch-policyd.service

%postun server
%systemd_postun_with_restart mediaconch-policyd.service
%endif

%files
%defattr(-,root,root,-)
%doc Release/ReadMe_CLI_Linux.txt History_CLI.txt
%if 0%{?fedora} || 0%{?centos_version} >= 700 || 0%{?rhel_version} >= 700
%license License.html License.GPLv3.html License.MPLv2.html
%else
%doc License.html License.GPLv3.html License.MPLv2.html
%endif
%{_bindir}/mediaconch-policy

%if 0%{?build_server}
%files server
%defattr(-,root,root,-)
%doc Documentation/Daemon.md Documentation/Config.md Documentation/REST.md
%if 0%{?fedora} || 0%{?centos_version} >= 700 || 0%{?rhel_version} >= 700
%license License.html License.GPLv3.html License.MPLv2.html
%else
%doc License.html License.GPLv3.html License.MPLv2.html
%endif
%{_bindir}/mediaconch-policyd
%if 0%{?fedora}
%config(noreplace) %{_sysconfdir}/%{name}/MediaConch.rc
%{_unitdir}/mediaconch-policyd.service
%endif
%endif # Server

%if 0%{?build_gui}
%files gui
%defattr(-,root,root,-)
%doc Release/ReadMe_GUI_Linux.txt History_GUI.txt
%if 0%{?fedora} || 0%{?centos_version} >= 700 || 0%{?rhel_version} >= 700
%license License.html License.GPLv3.html License.MPLv2.html
%else
%doc License.html License.GPLv3.html License.MPLv2.html
%endif
%{_bindir}/mediaconch-policy-gui
%{_datadir}/applications/*.desktop
%{_datadir}/pixmaps/*.png
%dir %{_datadir}/icons/hicolor
%dir %{_datadir}/icons/hicolor/256x256
%dir %{_datadir}/icons/hicolor/256x256/apps
%{_datadir}/icons/hicolor/256x256/apps/*.png
%dir %{_datadir}/apps
%dir %{_datadir}/apps/konqueror
%dir %{_datadir}/apps/konqueror/servicemenus
%{_datadir}/apps/konqueror/servicemenus/*.desktop
%dir %{_datadir}/kde4
%dir %{_datadir}/kde4/services
%dir %{_datadir}/kde4/services/ServiceMenus
%{_datadir}/kde4/services/ServiceMenus/*.desktop
%dir %{_datadir}/appdata
%{_datadir}/appdata/*.xml
%endif # GUI

%changelog
* Mon May 25 2015 MediaArea.net SARL <info@mediaarea.net> - %{mediaconch_version}
- See History.txt for more info and real dates

# Contributor: Vascom, vascom2@gmail.com"
