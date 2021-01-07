import logo from './logo.svg'
import react, { Component } from 'react';
import './App.css';
import ReactDOM from 'react-dom'
import io from 'socket.io-client'
import ConnectedUsers from '/Users/alireza/Desktop/Code/991/Internet Engineering/HW4/HW4/front/src/connectedUsers.js'

class Game extends Component {
  constructor() {
    super()
    this.state = { products: [] }
  }

  componentDidMount() {
    var socket = io.connect('http://127.0.0.1:5000');
    socket.on('playerList', this.handleData)
  }
  
  handleData = (productsList) => {
    this.setState({products: productsList})
  }

  render() {

    return(
      <div>
        <ConnectedUsers list={this.state.players}/>
      </div>
    )
  }
}

export default Game;

