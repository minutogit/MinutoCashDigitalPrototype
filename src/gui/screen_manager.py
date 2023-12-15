# screenmanager.py

from src.services.crypto_utils import generate_seed
from src.services.utils import is_password_valid
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.properties import StringProperty
from src.gui.user_info_screen import UserInfoScreen
from src.models.user_profile import user_profile

# Load the GUI layout files
Builder.load_file('gui/gui_layout.kv')
Builder.load_file('gui/user_info_screen.kv')

class NoProfileStartupScreen(Screen):
    """Screen displayed when no user profile is found."""
    pass

class DashboardScreen(Screen):
    """Dashboard screen displaying user's information."""
    # Properties for automatic update of values
    title = StringProperty('')
    balance_other_vouchers = StringProperty('')
    balance_own_vouchers = StringProperty('')

    def __init__(self, **kw):
        super().__init__(**kw)

    def on_enter(self):
        """Update the screen when entering."""
        self.title = self.get_title()
        self.balance_other_vouchers = str(self.get_balance_other_vouchers())
        self.balance_own_vouchers = str(self.get_balance_own_vouchers())

    def get_title(self):
        """Get the user's full name for the title."""
        name = user_profile.person_data['first_name']
        surname = user_profile.person_data['last_name']
        return f"{name} {surname}"

    def get_balance_other_vouchers(self):
        """Demo function to get balance of other vouchers."""
        return "123.45"

    def get_balance_own_vouchers(self):
        """Demo function to get balance of own vouchers."""
        return "500.00"


class ProfileLoginScreen(Screen):
    """Screen for logging into an existing user profile."""
    def __init__(self, **kw):
        super().__init__(**kw)

    def load_existing_profile(self, password):
        """Load an existing profile with the given password."""
        return user_profile.init_existing_profile(password)


class GenerateNewUserProfileScreen(Screen):
    """Screen for generating a new user profile."""
    def __init__(self, **kw):
        super().__init__(**kw)
        self.on_enter = self.init_seed

    def init_seed(self):
        self.generate_seed()

    def generate_seed(self):
        seed = generate_seed()
        self.ids.seed_field.text = seed

    def is_password_valid(self,password):
        return is_password_valid(password)

    def generate_new_user_profile(self, first_name, last_name, organization, seed, profile_password):
        """Create a new user profile with the given details."""
        user_profile.create_new_profile(first_name, last_name, organization, seed, profile_password)


# Main Application
class MyApp(MDApp):
    """Main application class."""
    def build(self):
        """Build the app's screen manager."""
        sm = ScreenManager(transition=SlideTransition(direction='left'))

        # Add screens based on whether a user profile exists
        if user_profile.profile_exists():
            sm.add_widget(ProfileLoginScreen(name='profile_login'))
            sm.current = 'profile_login'
        else:
            sm.add_widget(NoProfileStartupScreen(name='no_profile_startup'))
            sm.add_widget(GenerateNewUserProfileScreen(name='generate_new_user_profile'))
            sm.current = 'no_profile_startup'

        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(UserInfoScreen(name='user_info'))

        return sm

if __name__ == '__main__':
    MyApp().run()
