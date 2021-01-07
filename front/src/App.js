import logo from './logo.svg'
import react, { Component } from 'react';
import './App.css';
import ReactDOM from 'react-dom'
import io from 'socket.io-client'
import { Button } from 'semantic-ui-react'

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
