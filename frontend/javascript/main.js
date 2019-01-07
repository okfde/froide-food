import '../styles/main.scss'

import Vue from 'vue'
import VueLazyload from 'vue-lazyload'

import {renderComponent} from 'froide/frontend/javascript/lib/vue-helper'

import FoodMap from './components/food-map'

Vue.use(VueLazyload, {
  lazyComponent: true
})

Vue.config.productionTip = false

function createFoodMap (selector) {
  /* eslint-disable no-new */
  new Vue({
    components: { FoodMap },
    render: renderComponent(selector, FoodMap)
  }).$mount(selector)
}

document.addEventListener('DOMContentLoaded', function () {
  createFoodMap('#food-component')
})

export default {
  createFoodMap
}
