
class geeks:
    course = 'DSA'
    def purchase(obj):
        print("Purchase course : ", obj.course)
        return "a"

geeks.purchase = classmethod(geeks.purchase)
print(geeks.purchase())
print("aaaaaa")
geeks.purchase()