import '../styles/main.scss'

import Vue from 'vue'
import VueLazyload from 'vue-lazyload'

import FoodMap from './components/food-map'

Vue.use(VueLazyload)

Vue.config.productionTip = false

function createFoodMap (selector, config) {
  /* eslint-disable no-new */
  new Vue({
    data: {
      config: config
    },
    components: { FoodMap },
    el: selector
  })
}

module.exports = {
  createFoodMap
}
export default module.exports
