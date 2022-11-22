var update_btns = document.getElementsByClassName('update-cart')

for (i = 0; i < update_btns.length; i++){
    update_btns[i].addEventListener('click', function(){

        var product_id = this.dataset.product
        var action = this.dataset.action
        console.log('product_id:', product_id, 'action:', action)
    

        console.log('USER:', user)
        if(user === 'AnonymousUser'){
            add_cookie_item(product_id, action)
        }
        else
        {
            update_user_order(product_id, action)
        }
    })
}

function add_cookie_item(product_id, action){
   //not logged in
    if (action == 'add'){
		if (cart[product_id] == undefined){
		cart[product_id] = {'quantity':1}

		}else{                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
			cart[product_id]['quantity'] += 1
		}
	}
	if (action == 'remove'){
		cart[product_id]['quantity'] -= 1

		if (cart[product_id]['quantity'] <= 0){
			delete cart[product_id];
		}
	}
	console.log('CART:', cart)
	document.cookie ='cart=' + JSON.stringify(cart) + ";domain=;path=/"
	
	location.reload()
}

function update_user_order(product_id, action){
    console.log('user is logged in')

    var url = '/update_item'

    fetch(url,{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json', 
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({'product_id': product_id, 'action': action })    
    })

    .then((response) =>{
        return response.json()
    })

    .then((data) =>{
        console.log('data:', data)
        location.reload()
    })
}