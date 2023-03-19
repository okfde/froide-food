import '../styles/food.scss'

import VueLazyload from 'vue-lazyload'

import { createAppWithProps } from 'froide/frontend/javascript/lib/vue-helper'

import FoodMap from './components/food-map'

function createFoodMap(selector) {
  createAppWithProps(FoodMap, selector).use(VueLazyload).mount(selector)
}

document.addEventListener('DOMContentLoaded', function () {
  createFoodMap('#food-component')
})

export default {
  createFoodMap
}
