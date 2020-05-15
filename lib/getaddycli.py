import mm2lib

while True:
    time_lock = int(input("Input maker_payment_lock from Started e.g. 1588875030 : "))
    secret_hash = input("Input secret_hash e.g. bc88c6534d5b82866807cde2da0ce5735c335a2a : ")
    pub_0 = input("Input my_persistent_pub pubkey e.g. 03683c77e807a47dcd559fa60a6510087e5c5aa0016c094cf5eb4d7e002db18e9f : ")
    pub_1 = input("Input taker_pubkey from Negotiated event e.g. 032eadab416e372d21d8cbf798019325088dc796fd6762b6304c0298f279d58038 : ")
    print("Address: " + mm2lib.get_payment_address(time_lock, bytes.fromhex(secret_hash), bytes.fromhex(pub_0), bytes.fromhex(pub_1)))
