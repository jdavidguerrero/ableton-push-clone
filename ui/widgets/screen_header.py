from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.app import App

class ScreenHeader(BoxLayout):
    title = StringProperty("Clip View")
    info = StringProperty("Scene 1 / Track 1")
    
    def close_app(self):
        """Close the application"""
        app = App.get_running_app()
        if app and hasattr(app, 'close_app'):
            app.close_app()
        else:
            # Fallback
            app.stop()
