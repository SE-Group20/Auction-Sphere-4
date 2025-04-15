import pytest

# Sample logic to test
class Auction:
    def __init__(self, title, start_price):
        self.title = title
        self.start_price = start_price
        self.bids = []
        self.closed = False

    def place_bid(self, user, amount):
        if self.closed:
            return "Auction closed"
        if self.bids and amount <= self.bids[-1][1]:
            return "Bid too low"
        self.bids.append((user, amount))
        return "Bid accepted"

    def close_auction(self):
        self.closed = True
        return "Auction closed"

    def get_winner(self):
        if not self.closed or not self.bids:
            return None
        return self.bids[-1][0]

# ----------- Tests ------------
def test_auction_creation():
    auction = Auction("Bike", 50)
    assert auction.title == "Bike"
    assert auction.start_price == 50
    assert not auction.closed

def test_bid_higher_than_start_price():
    auction = Auction("Phone", 100)
    result = auction.place_bid("Alice", 120)
    assert result == "Bid accepted"
    assert auction.bids[-1] == ("Alice", 120)

def test_bid_too_low():
    auction = Auction("Watch", 200)
    auction.place_bid("Bob", 250)
    result = auction.place_bid("Charlie", 220)
    assert result == "Bid too low"
    assert auction.bids[-1] == ("Bob", 250)

def test_bid_after_closure():
    auction = Auction("Camera", 300)
    auction.close_auction()
    result = auction.place_bid("Dana", 350)
    assert result == "Auction closed"

def test_close_auction():
    auction = Auction("Book", 25)
    result = auction.close_auction()
    assert result == "Auction closed"
    assert auction.closed

def test_get_winner_none_if_open():
    auction = Auction("Tablet", 100)
    auction.place_bid("Eve", 150)
    assert auction.get_winner() is None

def test_get_winner_if_closed():
    auction = Auction("TV", 500)
    auction.place_bid("Frank", 600)
    auction.place_bid("Grace", 650)
    auction.close_auction()
    assert auction.get_winner() == "Grace"

def test_no_bids_returns_none():
    auction = Auction("Shoes", 75)
    auction.close_auction()
    assert auction.get_winner() is None

# 9. Test same user multiple bids
def test_same_user_multiple_bids():
    auction = Auction("Art", 100)
    auction.place_bid("Alex", 120)
    auction.place_bid("Alex", 140)
    assert auction.bids[-1] == ("Alex", 140)
    assert len(auction.bids) == 2

# 10. Test multiple users bidding
def test_multiple_users_bidding():
    auction = Auction("Laptop", 800)
    auction.place_bid("A", 850)
    auction.place_bid("B", 900)
    auction.place_bid("C", 950)
    assert auction.bids[-1][0] == "C"
    assert auction.bids[-1][1] == 950

# 11. Test bid equals to previous bid
def test_equal_bid_rejected():
    auction = Auction("Headphones", 60)
    auction.place_bid("X", 80)
    result = auction.place_bid("Y", 80)
    assert result == "Bid too low"
    assert len(auction.bids) == 1

# 12. Test no winner if not closed
def test_winner_none_if_not_closed():
    auction = Auction("Painting", 1000)
    auction.place_bid("Sam", 1200)
    assert auction.get_winner() is None

# 13. Test auction title type
def test_auction_title_type():
    auction = Auction("Sneakers", 300)
    assert isinstance(auction.title, str)

# 14. Test bid amount type
def test_bid_amount_type():
    auction = Auction("PS5", 400)
    auction.place_bid("User1", 420)
    assert isinstance(auction.bids[0][1], int)

# 15. Test auction start price must be positive
def test_start_price_positive():
    auction = Auction("Xbox", 0)
    assert auction.start_price == 0

# 16. Test closing auction prevents more bids
def test_bid_after_close_rejected():
    auction = Auction("Printer", 200)
    auction.place_bid("U1", 220)
    auction.close_auction()
    result = auction.place_bid("U2", 240)
    assert result == "Auction closed"

# 17. Test bid history grows correctly
def test_bid_history_length():
    auction = Auction("Backpack", 50)
    auction.place_bid("Tom", 60)
    auction.place_bid("Jerry", 70)
    assert len(auction.bids) == 2

# 18. Test closing auction twice has no extra effect
def test_double_close():
    auction = Auction("Board Game", 45)
    auction.close_auction()
    assert auction.closed
    auction.close_auction()
    assert auction.closed  # Still closed, no exception

# 19. Test winner after multiple bids
def test_winner_multiple_bids():
    auction = Auction("Chess Set", 20)
    auction.place_bid("A", 25)
    auction.place_bid("B", 30)
    auction.place_bid("C", 35)
    auction.close_auction()
    assert auction.get_winner() == "C"

# 20. Test winner is None when auction never opened
def test_never_opened_never_bid():
    auction = Auction("Unlisted", 100)
    auction.close_auction()
    assert auction.get_winner() is None

