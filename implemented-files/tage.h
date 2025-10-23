#ifndef BRANCH_TAGE_H
#define BRANCH_TAGE_H

#include <array>
#include <cmath>
#include <bitset>
#include <vector>
#include <deque>
#include <random>
#include "address.h"
#include "modules.h"
#include "../bimodal/bimodal.h"
#include "../gshare/gshare.h"
#include "../perceptron/perceptron.h"
#include "../hashed_perceptron/hashed_perceptron.h"
#include <iostream>
#include "./tage_config.h"


class tage : champsim::modules::branch_predictor
{
  //hyper parameters
  static constexpr std::size_t NUMBER_OF_TABLES = tage_config::NUMBER_OF_TABLES;

  //shortest history length + common ratio
  static constexpr uint16_t LEAST_HISTORY_LENGTH = tage_config::LEAST_HISTORY_LENGTH;
  static constexpr double COMMON_RATIO = tage_config::COMMON_RATIO;

  //max and min for u, pred, alt_better_than_pred
  static constexpr uint8_t U_MAX = 3;
  static constexpr uint8_t U_MIN = 0;
  static constexpr uint8_t PRED_MAX = 7;
  static constexpr uint8_t PRED_MIN = 0;
  static constexpr uint8_t ALT_BETTER_THAN_PRED_MAX = 15;
  static constexpr uint8_t ALT_BETTER_THAN_PRED_MIN = 0;

  //max and min for tag sizes
  static constexpr uint8_t TAG_SIZE_MAX = tage_config::TAG_SIZE_MAX;
  static constexpr uint8_t TAG_SIZE_MIN = tage_config::TAG_SIZE_MIN;

  //parameters for table sizes
  static constexpr uint8_t MAX_TABLE_SIZE_LOG = tage_config::MAX_TABLE_SIZE_LOG;
  static constexpr uint8_t MIN_TABLE_SIZE_LOG = tage_config::MIN_TABLE_SIZE_LOG;

  //total GHR length
  static constexpr std::size_t GHR_SIZE = 5000;

  //reset rate
  static constexpr uint32_t RESET_RATE = 256000;
  //base predictor
  bimodal base_predictor;
  //gshare base_predictor;
  //perceptron base_predictor;
  //hashed_perceptron base_predictor;
//-------------------------------------------------------------------

  //an integer to count how many times altpred is better than pred
  uint8_t alt_better_than_pred_count = 0;

  //reset counter
  uint32_t reset_counter = 0;
  uint8_t is_MSB = 1;

  //enum for table size change types
static constexpr tage_config::TableSizePattern ACTIVE_PATTERN = tage_config::ACTIVE_PATTERN;

  //struct for cells of tables
  struct cell {
    uint8_t u;
    uint8_t pred;
    uint32_t tag;
    cell(): u(0), pred(4), tag(0){}
  };

  struct circular_fold {
    uint16_t history_length;
    uint8_t target_size;
    uint32_t folded_value = 0;
  };

  //both, if not exist, will be -1
  int8_t provider_table_number;
  int8_t alternative_table_number;
  //indexes in porvider and alternative
  uint32_t index_in_provider;
  uint32_t index_in_alternative;
  //predictions, if not exist, false
  bool provider_prediction;
  bool alternative_prediction;
  //overall prediction
  bool overall_pred;
  
  std::array<uint16_t, tage::NUMBER_OF_TABLES> history_lengths = {};
  std::array<uint8_t, tage::NUMBER_OF_TABLES> tag_sizes = {};
  std::array<uint8_t, tage::NUMBER_OF_TABLES> table_sizes_log = {};
  std::array<circular_fold, tage::NUMBER_OF_TABLES> index_folds;
  std::array<circular_fold, tage::NUMBER_OF_TABLES> tag_folds1;
  std::array<circular_fold, tage::NUMBER_OF_TABLES> tag_folds2;
  std::array<uint32_t, NUMBER_OF_TABLES> indexes;
  std::array<uint32_t, NUMBER_OF_TABLES> tags;
  std::bitset<GHR_SIZE> global_history = 0;
  std::vector<std::vector<tage::cell>> tage_tables;
  std::mt19937 allocation_rng;     //used to generate a random choose between available tables to allocate

  public:
  using branch_predictor::branch_predictor;

  bool predict_branch(champsim::address ip);
  void last_branch_result(champsim::address ip, champsim::address branch_target, bool taken, uint8_t branch_type);

  tage(O3_CPU* cpu): branch_predictor(cpu), base_predictor(cpu){
    history_lengths[0] = tage::LEAST_HISTORY_LENGTH;
        for(size_t i = 1; i < NUMBER_OF_TABLES; i++) {
          history_lengths[i] = static_cast<uint16_t>(std::round(history_lengths[i-1] * tage::COMMON_RATIO));
        }

        //tag size decay step
        double step = static_cast<double>(tage::TAG_SIZE_MAX - tage::TAG_SIZE_MIN) / (tage::NUMBER_OF_TABLES - 1);
        for(size_t i =0; i < NUMBER_OF_TABLES; i ++) {
          tag_sizes[i] = static_cast<uint8_t>(std::round(tage::TAG_SIZE_MAX - static_cast<double>(i) * step));
        }

               size_t mid_point = NUMBER_OF_TABLES / 2;
       switch (ACTIVE_PATTERN) {
         case tage_config::TableSizePattern::CONSTANT:
          for (size_t i = 0; i < NUMBER_OF_TABLES; i++) {
            table_sizes_log[i] = MIN_TABLE_SIZE_LOG;
        }
        break;

       case tage_config::TableSizePattern::ASCENDING:
         for (size_t i = 0; i < NUMBER_OF_TABLES; i++) {
            double factor = static_cast<double>(MAX_TABLE_SIZE_LOG - MIN_TABLE_SIZE_LOG) / (NUMBER_OF_TABLES - 1);
            table_sizes_log[i] = static_cast<uint8_t>(std::round(MIN_TABLE_SIZE_LOG + static_cast<double>(i) * factor));
         }
         break;

    case tage_config::TableSizePattern::DESCENDING:
        for (size_t i = 0; i < NUMBER_OF_TABLES; i++) {
           double factor = static_cast<double>(MAX_TABLE_SIZE_LOG - MIN_TABLE_SIZE_LOG) / (NUMBER_OF_TABLES - 1);
           table_sizes_log[i] = static_cast<uint8_t>(std::round(MAX_TABLE_SIZE_LOG -  static_cast<double>(i)  * factor));
        }
        break;

    case tage_config::TableSizePattern::HILL_SHAPED:
        for (size_t i = 0; i <= mid_point; i++) {
            double factor = static_cast<double>(MAX_TABLE_SIZE_LOG - MIN_TABLE_SIZE_LOG) / static_cast<double>(mid_point);
            table_sizes_log[i] = static_cast<uint8_t>(std::round(MIN_TABLE_SIZE_LOG +  static_cast<double>(i)  * factor));
        }
        for (size_t i = mid_point + 1; i < NUMBER_OF_TABLES; i ++ ) {
            double factor = static_cast<double>(MAX_TABLE_SIZE_LOG - MIN_TABLE_SIZE_LOG) / static_cast<double>(NUMBER_OF_TABLES - mid_point  - 1);
            table_sizes_log[i] = static_cast<uint8_t>(std::round(MAX_TABLE_SIZE_LOG -  factor * static_cast<double>(i - mid_point)));
        }
        break;
    }

        tage_tables.resize(tage::NUMBER_OF_TABLES);
        for(size_t i = 0; i < tage::NUMBER_OF_TABLES; i++) {
          tage_tables[i].resize((1<<table_sizes_log[i]));
        }

        for(size_t i = 0; i < NUMBER_OF_TABLES; i++) {
          index_folds[i].history_length = tag_folds1[i].history_length = tag_folds2[i].history_length = history_lengths[i];
          index_folds[i].target_size = table_sizes_log[i];
          tag_folds1[i].target_size = tag_sizes[i];
          tag_folds2[i].target_size = tag_sizes[i] - 1;
        }
            
  }

};

#endif