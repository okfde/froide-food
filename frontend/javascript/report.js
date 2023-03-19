import { createAppWithProps } from 'froide/frontend/javascript/lib/vue-helper'

import FoodReport from './report/food-report'

Vue.config.productionTip = false

function createFoodReport(selector) {
  createAppWithProps(selector, FoodReport).mount(selector)
}

document.addEventListener('DOMContentLoaded', function () {
  createFoodReport('#food-report')
})

export default {
  createFoodReport
}
