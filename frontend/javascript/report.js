import Vue from 'vue'

import { renderComponent } from '~froide/frontend/javascript/lib/vue-helper'

import FoodReport from './report/food-report'

Vue.config.productionTip = false

function createFoodReport(selector) {
  /* eslint-disable no-new */
  new Vue({
    components: { FoodReport },
    render: renderComponent(selector, FoodReport)
  }).$mount(selector)
}

document.addEventListener('DOMContentLoaded', function () {
  createFoodReport('#food-report')
})

export default {
  createFoodReport
}
