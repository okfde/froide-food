import '../styles/food.scss'

import { createAppWithProps } from 'froide/frontend/javascript/lib/vue-helper'

import FoodMap from './components/food-map'

function createFoodMap(selector) {
  createAppWithProps(selector, FoodMap).mount(selector)
}

document.addEventListener('DOMContentLoaded', function () {
  createFoodMap('#food-component')
})

export default {
  createFoodMap
}
