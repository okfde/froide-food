import '../styles/food.scss'

import { createAppWithProps } from 'froide/frontend/javascript/lib/vue-helper'

import store from 'froide/frontend/javascript/store'

import FoodMap from './components/food-map'

function createFoodMap(selector) {
  createAppWithProps(selector, FoodMap).use(store).mount(selector)
}

document.addEventListener('DOMContentLoaded', function () {
  createFoodMap('#food-component')
})

export default {
  createFoodMap
}
