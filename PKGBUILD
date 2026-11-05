# Maintainer: DistroLinux Contributors <maintainers@example.invalid>
pkgname=distrolinux
pkgver=0.1.0
pkgrel=1
pkgdesc='Linux environment readiness checker'
arch=('any')
url='https://github.com/nhnhyhoom0-bot/sahab-lab-7kq'
license=('custom:UNLICENSED')
depends=('python')
source=("${pkgname}::git+https://github.com/nhnhyhoom0-bot/sahab-lab-7kq.git#commit=6e70f5645ad97124c25e374bb31b552abe28ba4f")
sha256sums=('SKIP')

package() {
  install -Dm755 "$srcdir/$pkgname/distrolinux.py" "$pkgdir/usr/lib/distrolinux/distrolinux.py"
  install -dm755 "$pkgdir/usr/bin"
  cat > "$pkgdir/usr/bin/distrolinux" <<'EOF'
#!/bin/sh
exec /usr/bin/python /usr/lib/distrolinux/distrolinux.py "$@"
EOF
  chmod 755 "$pkgdir/usr/bin/distrolinux"
}
