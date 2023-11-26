# person.py
import base64

from src.models.key import Key
from src.models.vouchertransaction import VoucherTransaction
from src.models.usertransaction import UserTransaction
from src.services.utils import get_timestamp, dprint
import json

class Person:
    def __init__(self, name, address, gender, email, phone, service_offer, coordinates, seed=None):
        self.key = Key(seed) if seed else Key()
        self.id = self.key.id
        self.pubkey_short = self.key.get_compressed_public_key()
        self.name = name
        self.address = address
        self.gender = gender  # 0 für unbekannt, 1 für männlich, 2 für weiblich
        self.email = email
        self.phone = phone
        self.service_offer = service_offer  # Angebot / Fähigkeiten
        self.coordinates = coordinates

        self.current_voucher = None  # Initialisierung von current_voucher
        self.vouchers = [] # list of vouchers
        self.usertransaction = UserTransaction()

    def init_empty_voucher(self):
        from src.models.minuto_voucher import MinutoVoucher
        self.current_voucher = MinutoVoucher()

    def create_voucher(self, amount, region, validity):
        """ Erstellt einen neuen MinutoVoucher. """
        from src.models.minuto_voucher import MinutoVoucher
        self.current_voucher = MinutoVoucher.create(self.id, self.name, self.address, self.gender, self.email, self.phone, self.service_offer, self.coordinates, amount, region, validity)

    def read_voucher_and_save_voucher(self, filename, subfolder=None, simulation = False):
        """read the voucher and stores it to persons voucher list"""
        self.read_voucher(filename, subfolder, simulation)
        self.vouchers.append(self.current_voucher)

    def read_voucher(self, filename, subfolder=None, simulation = False):
        """read the voucher"""
        self.init_empty_voucher()
        self.current_voucher = self.current_voucher.read_from_file(filename, subfolder, simulation)

    def save_voucher(self, filename = None, subfolder=None, simulation = False):
        return self.current_voucher.save_to_disk(filename, subfolder, simulation)

    def save_all_vouchers(self,filename):
        pass

    def sign_voucher_as_guarantor(self, voucher=None):
        """ Signs the voucher including the guarantor's personal details. """
        voucher = voucher or self.current_voucher

        if voucher.creator_id == self.id:
            print("Guarantors cannot sign their own vouchers.")
            return

        # Prepare guarantor information for signature
        guarantor_info = {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "gender": self.gender,
            "email": self.email,
            "phone": self.phone,
            "coordinates": self.coordinates,
            "signature_time": get_timestamp()
        }

        # Combine voucher data with guarantor information to create data for signing
        data_to_sign = voucher.get_voucher_data_for_signing() + json.dumps(guarantor_info, sort_keys=True)
        signature = self.key.sign(data_to_sign, base64_encode=True)

        # Append the signed guarantor information to the voucher
        voucher.guarantor_signatures.append((guarantor_info, signature))

    def verify_guarantor_signatures(self, voucher=None):
        """ Validates all guarantor signatures on the voucher. """
        voucher = voucher or self.current_voucher
        return voucher.verify_all_guarantor_signatures(voucher)

    def sign_voucher_as_creator(self, voucher=None):
        """ Signs the voucher as its creator and initialize the transaction list"""
        voucher = voucher or self.current_voucher

        if voucher.creator_id != self.id:
            print("Can only sign own voucher as creator!")
            return
        # Schöpfer signiert den Gutschein, inklusive der Bürgen-Signaturen
        data_to_sign = voucher.get_voucher_data_for_signing(include_guarantor_signatures=True)
        voucher.creator_signature = (self.key.sign(data_to_sign, base64_encode=True))
        # Initialize first transaction
        transaction = VoucherTransaction(voucher)
        transaction_data = transaction.get_initial_transaction(self.key)
        voucher.transactions.append(transaction_data)

    def verify_creator_signature(self, voucher=None):
        """ Verifies the signature of the voucher's creator. """
        voucher = voucher or self.current_voucher
        return voucher.verify_creator_signature(voucher)

    def send_amount(self, amount, recipient_id):
        """
        Send a specified amount to a person (recipient) using available vouchers.

        :param amount: The amount to send.
        :param recipient_id: The ID of the recipient.
        :return: List of vouchers used for the transaction.
        """
        return self.usertransaction.process_transaction_to_user(self, amount, recipient_id)

    def receive_amount(self, user_transaction):
        """
        Receives a transaction from another person, which may contain multiple vouchers,
        and stores these transactions in the recipient's own list of vouchers.

        This method takes a UserTransaction representing the incoming transaction,
        and appends the vouchers involved in this transaction to the recipient's voucher list.

        :param user_transaction: UserTransaction object containing the transaction details
                                 and the vouchers to be received.
        """
        self.usertransaction.receive_transaction_from_user(user_transaction, self)

    def list_vouchers(self):
        """prints a short list of all vouchers"""
        print("### Voucher List: ID -- Creator -- Available Amount ###")
        for voucher in self.vouchers:
            #dprint(voucher.get_voucher_amount(self.id))
            print(f"{voucher.voucher_id} -- {voucher.creator_name} -- {voucher.get_voucher_amount(self.id)}")

    def __str__(self):
        return f"Person({self.id}, {self.name}, {self.address}, {self.gender}, {self.email}, {self.phone}, {self.service_offer}, {self.coordinates})"
