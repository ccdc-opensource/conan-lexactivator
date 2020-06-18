import os
from conans import tools, ConanFile
from conans.errors import ConanInvalidConfiguration


class ConanLexActivator(ConanFile):
    name = "lexactivator"
    version = '3.9.2'
    description = "LexActivator licensing library"
    url = "https://app.cryptlex.com/downloads"
    homepage = "https://cryptlex.com/"
    topics = ("licensing", "cryptlex")
    license = "Proprietary"
    settings = "os", "compiler", "arch", "build_type"
    options = {
        "shared": [True, False],
    }
    default_options = {
        "shared": True,
    }

    @property
    def _la_libname(self):
        return 'LexActivator'
    
    def source(self):
        tools.get(**self.conan_data["sources"][self.version][str(self.settings.os)]['shared'])
        if self.settings.os == "Windows":
            tools.get(**self.conan_data["sources"][self.version][str(self.settings.os)]['static'][str(self.settings.compiler.version)])
        else:
            tools.get(**self.conan_data["sources"][self.version][str(self.settings.os)]['static'])

    @property
    def _package_lib_dir(self):
        if self.settings.os == 'Linux':
            compiler = 'gcc'
            la_arch = {
                'x86': 'i386',
                'x86_64': 'amd64',
                # TODO: map armv5el, armv5hf, armv6, armv7, armv7hf, armv7s, armv7k, armv8, armv8_32, armv8.3
                # to arm64, armel, armhf
            }[str(self.settings.arch)]
            return os.path.join('libs', compiler, la_arch)

        if self.settings.os == 'Windows':
            la_arch = {
                'x86': 'x86',
                'x86_64': 'x64',
            }[str(self.settings.arch)]
            if self.options.shared:
                if int(str(self.settings.compiler.version)) >= 16:
                    return os.path.join('libs', f'vc16', la_arch)
                else:
                    return os.path.join('libs', f'vc14', la_arch)
            else:
                if self.settings.compiler.runtime in ['MT', 'MTd']:
                    return os.path.join('libs', la_arch + '_MT')
                else:
                    return os.path.join('libs', la_arch)

        if self.settings.os == 'Macos':
            return os.path.join('libs', 'clang', 'x86_64')
        raise ConanInvalidConfiguration('Libraries for this configuration are not available')

    def package(self):
        self.copy("*.h", dst="include", src='headers')

        if self.options.shared:
            self.copy("*.dylib", dst="lib", src=self._package_lib_dir)
            self.copy("*.dll", dst="bin", src=self._package_lib_dir)
            self.copy("*.so", dst="lib", src=self._package_lib_dir)
            self.copy("LexActivator.lib", dst="lib", src=self._package_lib_dir)
        else:
            self.copy("*.a", dst="lib", src=self._package_lib_dir)
            if self.settings.compiler.runtime == 'MT':
                self.copy("LexActivator.lib", dst="lib", src=self._package_lib_dir)
                self.copy("libcurl_MT.lib", dst="lib", src=self._package_lib_dir)
            if self.settings.compiler.runtime == 'MTd':
                self.copy("LexActivatord.lib", dst="lib", src=self._package_lib_dir)
                self.copy("libcurl_MTd.lib", dst="lib", src=self._package_lib_dir)
            if self.settings.compiler.runtime == 'MD':
                self.copy("LexActivator.lib", dst="lib", src=self._package_lib_dir)
                self.copy("libcurl_MD.lib", dst="lib", src=self._package_lib_dir)
            if self.settings.compiler.runtime == 'MDd':
                self.copy("LexActivatord.lib", dst="lib", src=self._package_lib_dir)
                self.copy("libcurl_MDd.lib", dst="lib", src=self._package_lib_dir)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.settings.os == "Linux" and not self.options.shared:
            self.cpp_info.system_libs.extend(["pthread", "ssl3", "nss3", "nspr4"])
        if self.settings.os == "Macos" and not self.options.shared:
            self.cpp_info.frameworks.extend(["CoreFoundation", "SystemConfiguration", "Security"])
        if self.settings.os == "Windows" and self.options.shared:
            self.env_info.path.append(os.path.join(self.package_folder, "bin"))

        self.cpp_info.names["cmake_find_package"] = self._la_libname
        self.cpp_info.names["cmake_find_package_multi"] = self._la_libname

    def package_id(self):
        # we don't really care about the compiler version, unless we're on windows
        if self.settings.os != "Windows":
            self.info.settings.compiler.version = "any"