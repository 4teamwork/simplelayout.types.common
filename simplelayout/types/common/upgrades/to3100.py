from ftw.upgrade import UpgradeStep


class RemoveIcons(UpgradeStep):
    """Installs the profile which removes the icon expressions from simplelayout actions.
    """
    def __call__(self):
        self.setup_install_profile(
            'profile-simplelayout.types.common.upgrades:3100')
