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

// ADMIN

class App extends Component {
    constructor (props) {
        super(props);
        this.state = {
        products: [],
        cart: [],
        endpoint: "http://127.0.0.1:5000"
        }
        this.handleClick = this.handleClick.bind(this);
        this.handleClickRemove = this.handleClickRemove.bind(this);
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
        
        this.socket.on("update_prod",(data) => {
            this.setState({products: data})
            console.log(this.state.products);
        });
        
        this.socket.on("update_cart",(data) => {
            this.setState({cart: data})
            console.log(this.state.products);
        });
    }
    
    handleClick(e,idprod, nameprod, priceprod, quantprod) {
        e.preventDefault();
        this.socket.emit("modified-product", {id : idprod, name: nameprod, price: priceprod, quantity: quantprod}, function(idp){
            console.log(idprod);
            console.log(nameprod);
            console.log(priceprod);
            console.log(quantprod);
        });
      }

    handleClickRemove(e,idprod) {
        e.preventDefault();
        this.socket.emit("removed-product", {id : idprod}, function(idps){
            console.log(idprod);
        });
      }
    
    renderTableDataProducts(where) {
        return where.map((student, index) => {
            const { id, name, price, quantity } = student //destructuring
            const name_name = `${id}_name`;
            const name_price = `${id}_price`;
            const name_quant = `${id}_quant`;
            return (
                    <tr key={id}>
                    <td>{id}</td>
                    <td><input type="text" name={name_name} defaultValue={name}></input></td>
                    <td><input type="text" name={name_price} defaultValue={price}></input></td>
                    <td><input type="text" name={name_quant} defaultValue={quantity}></input></td>
                    <td><button key={id} width='50px' height='50px' onClick={(e) => this.handleClick(e,id,
                                                                                                     document.getElementsByName(name_name)[0].value,
                                                                                                     document.getElementsByName(name_price)[0].value,
                                                                                                     document.getElementsByName(name_quant)[0].value)}>Apply</button></td>
                    <td><button key={id} width='50px' height='50px' onClick={(e) => this.handleClickRemove(e,id)}>Remove</button></td>
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
                <h1 id='title'>Products List - Admin Panel</h1>
                <table id='students'>
                <tbody>
                <tr>{this.renderTableHeader(this.state.products)}</tr>
                {this.renderTableDataProducts(this.state.products)}
                </tbody>
                </table>
                </div>
                )
    }
}

ReactDOM.render(<table />, document.getElementById('root'));
export default App;
