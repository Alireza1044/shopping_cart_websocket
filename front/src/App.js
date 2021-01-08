import logo from './logo.svg';
import react, { Component } from 'react';
import './App.css';
import ReactDOM from 'react-dom';
import io from 'socket.io-client';
import { Button } from 'semantic-ui-react';
import Cookies from 'js-cookie';
import zlib from 'react-zlib-js';
import pako from 'pako';
import urlsafe_b64 from 'urlsafe-base64';
import { encode, decode, Base64 } from 'js-base64';

function getCookie(ca,name) {
    var nameEQ = name + "=";
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}

function readCookie(cname) {
  var name = cname + "=";
  var decodedCookie = decodeURIComponent(document.cookie);
  var ca = decodedCookie.split(';');
  for(var i = 0; i <ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

function bake_cookie(name, value) {
  var cookie = [name, '=', JSON.stringify(value), '; domain=.', window.location.host.toString(), '; path=/;'].join('');
  document.cookie = cookie;
}

class App extends Component {
  constructor (props) {
    super(props);
    this.state = {
      products: [],
      cart: [],
      endpoint: "http://127.0.0.1:5000"
    }
    this.handleClick = this.handleClick.bind(this);
    this.socket = io(this.state.endpoint)
  }


componentDidMount() {
  console.log('I was triggered during componentDidMount')
  const { endpoint } = this.state;

  fetch('http://127.0.0.1:5000/shop/',{method: 'GET',
  credentials: "include"})
        .then(response => response.json())
        .then(data => { this.setState({ products: data })
  console.log('products');
  console.log(this.state.products);
  console.log('data');
  console.log(this.data);
});
  
  console.log("coooooookie");
  let data = Cookies.get('session');
  console.log(data);
  var compressed = false;
  if (data){
  if (data.substring(0, 1) == "."){
    compressed = true;
    data = data.slice(1);
    console.log("SLiced");
    console.log(data);
  }
  data = data.split(".")[0];
  data = urlsafe_b64.decode(data);
  console.log(data);
  if (compressed){
  data = pako.inflate(data, { to: 'string' });
}
  data = JSON.parse(data);
  console.log(data);
  console.log("done");
  console.log(data.cart);
  this.setState({cart: data.cart})
}


  this.socket.on("update_prod",(data) => {
    this.setState({products: data})
    console.log(this.state.products);
   });

  this.socket.on("update_cart",(data) => {
    this.setState({cart: data})
    console.log(this.state.products);
   });
}

handleClick(e,idprod) {
    e.preventDefault();
    this.socket.emit("added-to-cart", {id : idprod}, function(idp){
    console.log(idprod);
  });
  }

  renderTableData(where) {
      return where.map((student, index) => {
         const { id, name, price, quantity } = student //destructuring
         return (
            <tr key={id}>
               <td>{id}</td>
               <td>{name}</td>
               <td>{price}</td>
               <td>{quantity}</td>
               <td><button key={id} width='50px' height='50px' onClick={(e) => this.handleClick(e,id)}>Add</button></td>
            </tr>
         )
      })
   }

   renderTableHeader(where) {
    if(where[0]){
      let header = Object.keys(where[0])
      return header.map((key, index) => {
         return <th key={index}>{key.toUpperCase()}</th>
      })
    }
   }

   render() {
      return (
         <div>
            <h1 id='title'>Products List</h1>
            <table id='students'>
               <tbody>
                  <tr>{this.renderTableHeader(this.state.products)}</tr>
                  {this.renderTableData(this.state.products)}
               </tbody>
            </table>

            <h1 id='title'>Shopping Cart</h1>
            <table id='students'>
               <tbody>
                  <tr>{this.renderTableHeader(this.state.cart)}</tr>
                  {this.renderTableData(this.state.cart)}
               </tbody>
            </table>
         </div>
      )
   }
 }
  
ReactDOM.render(<table />, document.getElementById('root'));
export default App;
