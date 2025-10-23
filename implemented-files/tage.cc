#include "tage.h"
#include <random>

bool tage::predict_branch(champsim::address ip) {
    size_t pc = ip.to<unsigned long>();
    //compute all tags and indexes
    for(size_t i = 0; i < NUMBER_OF_TABLES; i ++) {
        indexes[i] = static_cast<uint32_t>((pc ^ index_folds[i].folded_value) & ((1<< table_sizes_log[i]) -1 ));
        tags[i] = static_cast<uint32_t>(((pc >> 2)^ tag_folds1[i].folded_value ^ (tag_folds2[i].folded_value << 1)) & ((1 << tag_sizes[i]) - 1));
    }

    int8_t provider_table_num, alt_table_number;
    uint32_t index_in_prov, index_in_alt;
    bool provider_pred, alt_pred;
    bool is_newly_allocated;
    //------------------------------
    provider_table_num = alt_table_number = -1;
    is_newly_allocated = provider_pred = alt_pred = false;
    index_in_prov = index_in_alt = 0;
    //------------------------------
    for(int i = NUMBER_OF_TABLES - 1; i >= 0; i--) {
        uint32_t index = indexes[i];
        uint32_t tag = tags[i];
        uint32_t tag_in_table = tage_tables[i][index].tag;

        if(tag_in_table == tag && provider_table_num == -1) {
            provider_table_num = static_cast<uint8_t>(i);
            provider_pred = tage_tables[i][index].pred >= 4;
            index_in_prov = index;
            is_newly_allocated = (tage_tables[i][index].u == 0) && 
                (tage_tables[i][index].pred == 3 || tage_tables[i][index].pred == 4) && 
                alt_better_than_pred_count >= 8;
        } else if(tag_in_table == tag && alt_table_number == -1){
            alt_table_number = static_cast<uint8_t>(i);
            alt_pred = tage_tables[i][index].pred >= 4;
            index_in_alt = index;
            break;
        }
    }
    
    this->provider_table_number = provider_table_num;
    this->alternative_table_number = alt_table_number;
    this->index_in_provider = index_in_prov;
    this->index_in_alternative = index_in_alt;
    this->provider_prediction = provider_pred;
    this->alternative_prediction = alt_pred;
    bool prediction = false;

    if(provider_table_num == -1) {
        prediction = base_predictor.predict_branch(ip);
    }
    else if(is_newly_allocated && alt_table_number != -1) {
        prediction = alt_pred;
    }
    else {
        prediction = provider_pred;
    }
    
    this->overall_pred = prediction;
    return prediction;
}

void tage::last_branch_result(champsim::address ip, champsim::address branch_target, bool taken, uint8_t branch_type) {

    if(provider_table_number == -1) {
        base_predictor.last_branch_result(ip, branch_target, taken, branch_type);
    }
    else {
        cell& cell_in_provider = tage_tables[provider_table_number][index_in_provider];
        //update u
        if(alternative_table_number != -1) {
            if(alternative_prediction == taken && provider_prediction != taken && cell_in_provider.u > tage::U_MIN)
                cell_in_provider.u -= 1;
            else if(alternative_prediction != taken && provider_prediction == taken && cell_in_provider.u < tage::U_MAX)
                cell_in_provider.u += 1;
        }

        //update pred
        if(taken && cell_in_provider.pred < tage::PRED_MAX)
            cell_in_provider.pred += 1;
        else if(!taken && cell_in_provider.pred > tage::PRED_MIN)
            cell_in_provider.pred -= 1;
        
        //alt_better_than_pred_count update
        if(alternative_table_number != -1) {
            if(alternative_prediction == taken && provider_prediction != taken && alt_better_than_pred_count < ALT_BETTER_THAN_PRED_MAX)
                alt_better_than_pred_count += 1;
            else if(alternative_prediction != taken && provider_prediction == taken && alt_better_than_pred_count > ALT_BETTER_THAN_PRED_MIN)
                alt_better_than_pred_count -= 1;
        }
    }
    //allocation if needed
    if(taken != overall_pred) {
        std::vector<uint8_t> candidate_table_numbers;
        std::vector<uint32_t> corresponding_indexes;

        //list the candidtate tables for allocation
        for(int i = provider_table_number + 1; i < static_cast<int>(NUMBER_OF_TABLES); i++) {
            uint32_t index = indexes[i];
            if(tage_tables[i][index].u == 0) {
                candidate_table_numbers.push_back(static_cast<uint8_t>(i));
                corresponding_indexes.push_back(index);
            } 
        }

        //decrement u values if empty
        if(candidate_table_numbers.empty()) {
            for(int i = provider_table_number + 1; i < static_cast<int>(NUMBER_OF_TABLES); i++) {
                uint32_t index = tags[i];
                auto &u = tage_tables[i][index].u;
                if (u > U_MIN) u--;
            }
        }else {
                std::vector<double> prob_weights;
                for(size_t i =0; i < corresponding_indexes.size(); i++) {
                    prob_weights.push_back(1.0 / (1 << i));
                }
                std::discrete_distribution<> dist(prob_weights.begin(), prob_weights.end());

                int index_in_candidates = dist(allocation_rng);
                uint8_t chosen_number = candidate_table_numbers[index_in_candidates];
                uint32_t index_in_chosen = corresponding_indexes[index_in_candidates];

                tage_tables[chosen_number][index_in_chosen].pred = 4;
                tage_tables[chosen_number][index_in_chosen].tag = tags[chosen_number];
            }

    }
    //increment reset_counter and reset if needed
    reset_counter ++;
    size_t real_size;
    if(reset_counter == RESET_RATE) {
        for(size_t i = 0; i < NUMBER_OF_TABLES; i ++) {
            real_size = (1u << table_sizes_log[i]);
            for(size_t j =0; j < real_size; j++){
                tage_tables[i][j].u &= (is_MSB + 1);
            }
        }
        is_MSB = 1 - is_MSB;
        reset_counter = 0;
    }

    //update GHR
    global_history <<= 1;
    global_history.set(0, taken);

    //update circular_folds(recursively and without function call to speedup!)
    for(size_t i = 0; i < NUMBER_OF_TABLES; i++) {
        //index folds
        index_folds[i].folded_value = (index_folds[i].folded_value << 1) + global_history[0];
        index_folds[i].folded_value ^= ((index_folds[i].folded_value & (1 << index_folds[i].target_size)) >> index_folds[i].target_size);
        index_folds[i].folded_value ^= (global_history[index_folds[i].history_length] << (index_folds[i].history_length % index_folds[i].target_size));
        index_folds[i].folded_value &= ((1 << index_folds[i].target_size) -1);

        //tagfolds1
        tag_folds1[i].folded_value = (tag_folds1[i].folded_value << 1) + global_history[0];
        tag_folds1[i].folded_value ^= ((tag_folds1[i].folded_value & (1 << tag_folds1[i].target_size)) >> tag_folds1[i].target_size);
        tag_folds1[i].folded_value ^= (global_history[tag_folds1[i].history_length] << (tag_folds1[i].history_length % tag_folds1[i].target_size));
        tag_folds1[i].folded_value &= ((1 << tag_folds1[i].target_size) -1);

        //tagfolds2
        tag_folds2[i].folded_value = (tag_folds2[i].folded_value << 1) + global_history[0];
        tag_folds2[i].folded_value ^= ((tag_folds2[i].folded_value & (1 << tag_folds2[i].target_size)) >> tag_folds2[i].target_size);
        tag_folds2[i].folded_value ^= (global_history[tag_folds2[i].history_length] << (tag_folds2[i].history_length % tag_folds2[i].target_size));
        tag_folds2[i].folded_value &= ((1 << tag_folds2[i].target_size) -1);
    }
}