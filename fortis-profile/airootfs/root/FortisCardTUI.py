import urwid
import threading
import subprocess
from mnemonic import Mnemonic
import smartcard
from smartcard.System import readers
from CryptoUtils import store_encrypted_seed

class FortisCardTUI:
    def __init__(self):
        self.language = 'english'
        self.tweleve_word_mnemonic = True
        self.mnemonic = ''
        self.passphrase = ''
        self.setup_welcome_screen()


    def create_screen(self, widgets):
        '''Create a screen with header and footer
        Args:
            widgets (list): List of widgets to display between header and footer
        '''
        header = urwid.AttrMap(urwid.Padding(self.header, 'center'), 'header')
        footer = urwid.AttrMap(urwid.Padding(self.footer, 'center'), 'footer')

        # Add spacing around content
        content = [urwid.Divider()]
        for w in widgets:
            content.extend([w, urwid.Divider()])

        # Create the main content area with a border
        main_content = urwid.LineBox(
            urwid.Pile(content),
            title='FortisCard Setup'
        )

        # Combine everything with proper spacing
        screen = urwid.Pile([
            ('pack', header),
            urwid.Divider(),
            ('weight', 1, main_content),
            urwid.Divider(),
            ('pack', footer)
        ])

        return urwid.Filler(screen, valign='top')


    def setup_welcome_screen(self):
        self.header = urwid.Text('Welcome to FortisCard Setup!')
        self.footer = urwid.Text('Navigate with arrow keys. Press Enter to select')
        self.body = self.create_screen([
            urwid.Text('Thank you for buying a FortisCard!', align='center'),
            urwid.Text('Please plug in your FortisCard to your computer with the provided card reader if not already.', align='center'),
            urwid.Button('Check for FortisCard', on_press=self.check_for_card),
        ])

        self.layout = self.body
        palette = [
            ('header', 'white,bold', 'dark blue'),
            ('footer', 'white,bold', 'dark blue'),
            ('button', 'white', 'dark green'),
            ('border', 'white', 'dark gray'),
        ]
        self.loop = urwid.MainLoop(self.layout, palette=palette)

    def set_layout(self, layout):
        self.layout = layout
        self.loop.widget = self.layout

    def setup_options_screen(self):
        self.body = self.create_screen([
            urwid.Text('Choose mnemonic length:', align='center'),
            urwid.Button('12 words (default)', on_press=self.set_mnemonic_length, user_data=True),
            urwid.Button('24 words', on_press=self.set_mnemonic_length, user_data=False),
        ])
        self.set_layout(self.body)


    def set_mnemonic_length(self, button, twelve_words):
        self.tweleve_word_mnemonic = twelve_words
        self.body = self.create_screen([
            urwid.Text('Choose your option:', align='center'),
            urwid.Button('Generate a new mnemonic', on_press=self.generate_mnemonic),
            urwid.Button('Input your own mnemonic', on_press=self.input_mnemonic),
        ])
        self.set_layout(self.body)


    def check_for_card(self, button):
        try:
            if not readers():
                self.body = self.create_screen([
                    urwid.Text('No FortisCard reader detected. Please connect your card reader and FortisCard.', align='center'),
                    urwid.Button('Check again', on_press=self.check_for_card),
                ])
            else:
                reader = readers()[0]
                self.connection = reader.createConnection()
                self.connection.connect()
                self.setup_options_screen()
        except smartcard.Exceptions.NoCardException:
            self.body = self.create_screen([
                urwid.Text('No FortisCard detected. Please connect your card.', align='center'),
                urwid.Button('Check again', on_press=self.check_for_card),
            ])
        except Exception as e:
            self.body = self.create_screen([
                urwid.Text(f'Error checking card: {str(e)}', align='center'),
                urwid.Button('Try again', on_press=self.check_for_card),
            ])
        finally:
            self.set_layout(self.body)


    def generate_mnemonic(self, button):
        passphrase_edit = urwid.Edit('Passphrase (optional): ')
        self.body = self.create_screen([
            urwid.Text('Enter an optional passphrase:', align='center'),
            passphrase_edit,
            urwid.Button('Generate', on_press=self.get_keyboard_entropy, user_data=passphrase_edit),
        ])
        self.set_layout(self.body)


    def get_keyboard_entropy(self, button, passphrase_edit):
        self.passphrase = passphrase_edit.edit_text

        self.body = self.create_screen([
            urwid.Text('Please type random keys to generate entropy', align='center'),
        ])
        self.set_layout(self.body)
        threading.Thread(target=self.do_generate_mnemonic).start()


    def do_generate_mnemonic(self):
        try:
            result = subprocess.run(['bip39', '-k', '-e', '128' if self.tweleve_word_mnemonic else '256', '-l', self.language, '-p', self.passphrase], capture_output=True, text=True)
            self.mnemonic = result.stdout.strip().splitlines()[1]

            if self.passphrase:
                self.body = self.create_screen([
                    urwid.Text('Your generated mnemonic (write this down):', align='center'),
                    urwid.Text(self.mnemonic, align='center'),
                    urwid.Text('Your passphrase (write this down somewhere else):', align='center'),
                    urwid.Text(self.passphrase, align='center'),
                    urwid.Button('Continue', on_press=self.get_pin),
                ])
            else:
                self.body = self.create_screen([
                    urwid.Text('Your generated mnemonic (write this down):', align='center'),
                    urwid.Text(self.mnemonic, align='center'),
                    urwid.Button('Continue', on_press=self.get_pin),
                ])
        except Exception as e:
            self.body = self.create_screen([
                urwid.Text(f'Error generating mnemonic: {str(e)}', align='center'),
            ])
        finally:
            self.set_layout(self.body)


    def input_mnemonic(self, button):
        mnemonic_edit = urwid.Edit('Mnemonic: ')
        passphrase_edit = urwid.Edit('Passphrase (optional): ')

        self.body = self.create_screen([
            mnemonic_edit,
            passphrase_edit,
            urwid.Button('Submit', on_press=self.process_input_mnemonic, user_data=(mnemonic_edit, passphrase_edit)),
        ])
        self.set_layout(self.body)


    def process_input_mnemonic(self, button, user_data):
        mnemonic_edit, passphrase_edit = user_data
        try:
            mnemo = Mnemonic(self.language)
            if not mnemo.check(mnemonic_edit.edit_text):
                raise ValueError('Invalid mnemonic phrase')

            # Set the values from the edit widgets
            self.mnemonic = mnemonic_edit.edit_text
            self.passphrase = passphrase_edit.edit_text
            self.get_pin(button)
        except Exception as e:
            self.body = self.create_screen([
                urwid.Text(f'Error: {str(e)}', align='center'),
                urwid.Button('Try again', on_press=self.input_mnemonic),
            ])
            self.set_layout(self.body)


    def get_pin(self, button):
        # Pin will be stored as one byte per character
        pin_edit = urwid.Edit('Enter your 6-digit PIN: ')
        self.body = self.create_screen([
            urwid.Text('Enter your PIN to encrypt the seed:', align='center'),
            pin_edit,
            urwid.Button('Submit and wait', on_press=self.process_pin, user_data=pin_edit),
        ])
        self.set_layout(self.body)


    def process_pin(self, button, pin_edit):
        try:
            self.pin = pin_edit.edit_text
            if len(self.pin) != 6 or not self.pin.isdigit():
                raise ValueError('PIN must be a 6-digit number')

            self.send_seed_to_fortis_card()
        except Exception as e:
            self.body = self.create_screen([
                urwid.Text(f'Error processing PIN: {str(e)}', align='center'),
                urwid.Button('Try again', on_press=self.get_pin),
            ])
            self.set_layout(self.body)


    def send_seed_to_fortis_card(self):
        try:
            mnemo = Mnemonic(self.language)
            seed = mnemo.to_seed(self.mnemonic, self.passphrase).hex()
            store_encrypted_seed(self.connection, bytes.fromhex(seed), self.pin.encode())

            self.body = self.create_screen([
                urwid.Text('FortisCard successfully initialized! You may now unplug your card and USB with Fortis ISO and reboot/poweroff your computer.', align='center'),
            ])
        except Exception as e:
            self.body = self.create_screen([
                urwid.Text(f'Error Initializing FortisCard: {str(e)}', align='center'),
            ])
        finally:
            self.set_layout(self.body)

