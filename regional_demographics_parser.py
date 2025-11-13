def main(csvfile_1, csvfile_2):
    """Main function used to return all 3 expected outputs. Any invalid data and corner cases have been tackled in this function, before calculation of outputs."""
    
    # tries to open both files, assigning them to file1 and file2 variables
    try:
        file1 = open(csvfile_1, 'r')
        file2 = open(csvfile_2, 'r')
    except FileNotFoundError:
        print('One or both files were not found.')
        return {}, {}, {} # returns empty dictionaries for all 3 outputs
    except Exception:
        print(f'An error occurred while opening the files: {Exception}')
        return {}, {}, {} # returns empty dictionaries for all 3 outputs
    
    # empty lists to store file data
    data1 = []
    data2 = []

    # fills values1 to be a list of lists for first file
    values1 = []
    for row in file1:
        data1.append(row)
    for row in data1:
        line = row.strip().split(',') # .strip() used to remove \n and potential white spaces, separates each age_range by comma, embedding a new list in the values2 list
        line_lower = [column.strip().casefold() for column in line]
        if line_lower not in values1: # avoids duplicate rows
            values1.append(line_lower)

    # fills values2 to be a list of lists for second file
    values2 = []
    for row in file2:
        data2.append(row)
    for row in data2:
        line = row.strip().split(',') # .strip() used to remove \n and potential white spaces, separates each age_range by comma, embedding a new list in the values2 list
        line_lower = [column.strip().casefold() for column in line]
        if line_lower not in values2: # avoids duplicate rows
            values2.append(line_lower)
    
    # closes both files
    file1.close()
    file2.close()
    
    # possible case: files with only headers and no data, handled with graceful termination
    if len(values1) <= 1 or len(values2) <= 1:
        print('One or both input files do not contain any data.')
        return {}, {}, {}
    
    # possible case: files with missing columns, handled with graceful termination
    required_headers_file1 = ['s_t code', 's_t name', 'sa3 code', 'sa3 name', 'sa2 code', 'sa2 name']
    required_headers_file2 = ['area_code_level2', 'area_name_level2']
    missing_columns1 = []
    missing_columns2 = []
    
    for header in required_headers_file1:
        if header not in values1[0]:
            missing_columns1.append(header)
    for header in required_headers_file2:
        if header not in values2[0]:
            missing_columns2.append(header)
    
    # graceful termination
    if missing_columns1 or missing_columns2:
        print('Missing required columns:', ', '.join(missing_columns1), ', '.join(missing_columns2))
        return {}, {}, {} # returns empty dictionaries for all 3 outputs
    
    # compiles all column indices for each data file
    # file 1 column indices
    st_code_index = values1[0].index('s_t code')
    st_name_index = values1[0].index('s_t name')
    sa3_code_index = values1[0].index('sa3 code')
    sa3_name_index = values1[0].index('sa3 name')
    sa2_code_index_a = values1[0].index('sa2 code')
    sa2_name_index_a = values1[0].index('sa2 name')    
    
    # file 2 column indices
    sa2_code_index_p = values2[0].index('area_code_level2')
    sa2_name_index_p = values2[0].index('area_name_level2')
    
    # cleans up the values to avoid missing values and duplicate SA2 codes
    cleaned_values1 = []
    for row in values1[1:]:
        if all(str(column.strip()) != '' for column in row) and row not in cleaned_values1:
            cleaned_values1.append(row)
    values1 = [values1[0]] + cleaned_values1 # keeps the header
    
    cleaned_values2 = []
    for row in values2[1:]:
        invalid = False
        for column in row:
            if column != row[sa2_code_index_p] and column != row[sa2_name_index_p]:
                try:
                    if int(column) < 0: # skips negative populations
                        invalid = True
                except ValueError:
                    invalid = True # skips invalid variable types
                    break
        if invalid == False and all(column.strip() != '' for column in row):
            cleaned_values2.append(row)
    values2 = [values2[0]] + cleaned_values2 # keeps the header

    # possible case: population data is not provided for all SA2 areas, handled by matching values1 and values2 1:1 to avoid out-of-scope values and mismatches
    sa2_codes_areas = [row[sa2_code_index_a] for row in values1[1:]]
    sa2_codes_populations = [row[sa2_code_index_p] for row in values2[1:]]
    valid_codes = set(sa2_codes_areas).intersection(set(sa2_codes_populations))
            
    values1 = [values1[0]] + [row for row in values1[1:] if row[sa2_code_index_a] in valid_codes]
    values2 = [values2[0]] + [row for row in values2[1:] if row[sa2_code_index_p] in valid_codes]
    
    # lists for compiling all codes for each area type
    state_codes = []
    sa3_codes = []
    sa2_codes = []
    
    # compiles all state codes, SA3 area codes, and SA2 area codes into their respective lists
    for row in values1[1:]:
        if row[st_code_index] not in state_codes:
            state_codes.append(row[st_code_index])
        if row[sa3_code_index] not in sa3_codes:
            sa3_codes.append(row[sa3_code_index])
        if row[sa2_code_index_a] not in sa2_codes:
            sa2_codes.append(row[sa2_code_index_a])
    
    def age_group_populations():
        """Create a dictionary of the largest populations among each area type (state, SA2, SA3), for each age group"""
        
        result_dict = {}
        
        for i, heading in enumerate(values2[0]):
            current_range = []
            dict_value = []
            # only uses age headings, ignoring code and name columns
            if 'age' in heading:
                num = ''
                max_state_name = ''
                max_sa3_name = ''
                max_sa2_name = ''
                
                # creation of keys
                # creates a list of the age group bounds, to be added as keys to the result dictionary
                for char in heading:
                    if char.isdigit() == True:
                        num += char
                    elif char.isdigit() == False and num:
                        current_range.append(int(num))
                        num = ''
                
                # appends the last number in the heading if no characters follow
                if num: 
                    current_range.append(int(num))
                
                # get state with the largest population under current age group
                state_populations_dict = {}
                for num in state_codes:
                    summation = 0
                    for row in values2[1:]:
                        if row[sa2_code_index_p].startswith(num) == True:
                            summation += int(row[i])
                    state_populations_dict[num] = summation
                    state_populations_dict = dict(sorted(state_populations_dict.items(), key=lambda x: x[0])) # rearranges the dictionary in alphabetical order, since max() function gets the first instance of the largest value
                    for row in values1[1:]:
                        if row[st_code_index] == max(state_populations_dict, key=state_populations_dict.get):
                            max_state_name = row[st_name_index]
                            break
                
                # get SA3 area with the largest population under current age group
                sa3_populations_dict = {}
                for num in sa3_codes:
                    summation = 0
                    for row in values2[1:]:
                        if row[sa2_code_index_p].startswith(num) == True:
                            summation += int(row[i])
                    sa3_populations_dict[num] = summation
                    sa3_populations_dict = dict(sorted(sa3_populations_dict.items(), key=lambda x: x[0])) # rearranges the dictionary in alphabetical order, since max() function gets the first instance of the largest value
                    for row in values1[1:]:
                        if row[sa3_code_index] == max(sa3_populations_dict, key=sa3_populations_dict.get):
                            max_sa3_name = row[sa3_name_index]                            
                            break
                
                # get SA2 area with the largest population under current age group
                sa2_populations = []
                for num in sa2_codes:
                    for row in values2[1:]:
                        if num == row[sa2_code_index_p]:
                            sa2_populations.append((row[sa2_name_index_p], row[sa2_code_index_p], int(row[i])))
                    sa2_populations.sort(key=lambda x: x[1])
                    max_sa2_name = max(sa2_populations, key=lambda x: x[2])[0]
                
                dict_value = [max_state_name, max_sa3_name, max_sa2_name]
                
                # final step
                # adds items to the output dictionary for OP1, fulfilling the following conditions regarding the bounds of the given age groups
                if len(current_range) == 2:
                    result_dict[f'{current_range[0]}-{current_range[1]}'] = dict_value
                elif len(current_range) == 1 and 'over' in heading:
                    current_range.append(None)
                    result_dict[f'{current_range[0]}-{current_range[1]}'] = dict_value
                elif len(current_range) == 1 and 'under' in heading:
                    current_range.insert(0, None)
                    result_dict[f'{current_range[0]}-{current_range[1]}'] = dict_value
                else:
                    result_dict[None] = []

        return result_dict
    
    OP1 = age_group_populations()
    
    def state_population_stats():
        """Create a dictionary containing the population statistics for each state"""
        
        outer_dict = {}
        sa3_populations = []
        
        # gets total populations of each SA3 area
        for num in state_codes:
            inner_dict = {}
            for code in sa3_codes:
                summation = 0
                for row in values2[1:]:
                    if row[sa2_code_index_p].startswith(code) and row[sa2_code_index_p].startswith(num):
                        for column in row:
                            if column != row[sa2_code_index_p] and column != row[sa2_name_index_p]:
                                summation += int(column)
                
                # filters out SA3 areas with a population lower than 150000
                if summation >= 150000:
                    sa3_populations.append((code, summation))
                    
                    inner_list = []
                    sa2_populations = []
                    
                    # calculation of both population average and standard deviation
                    for row in values2[1:]:
                        sa2_summation = 0
                        total_count = 0
                        if row[sa2_code_index_p].startswith(code) and row[sa2_code_index_p].startswith(num): # checking if SA2 code belongs to the proper SA3 area and state
                            for column in row:
                                if column != row[sa2_code_index_p] and column != row[sa2_name_index_p]: # excludes code and name columns
                                    sa2_summation += int(column)
                                    total_count += 1
                            # prevention of division by zero
                            if total_count != 0:
                                average = sa2_summation / total_count
                            else:
                                average = 0
                            sd_summation = 0
                            for column in row:
                                if column != row[sa2_code_index_p] and column != row[sa2_name_index_p]: # excludes code and name columns
                                    deviation = (int(column) - average) ** 2
                                    sd_summation += deviation
                            # prevention of division by zero
                            if total_count != 1:
                                st_dev = (sd_summation / (total_count - 1)) ** 0.5
                            else:
                                st_dev = 0
                            sa2_populations.append((row[sa2_code_index_p], sa2_summation, round(st_dev, 4)))
                    
                    sa2_populations.sort(key=lambda x: x[0]) # sorts the dictionary in alphabetical order, according to the SA2 area code
                    
                    # creation of list to be used as values for the inner dictionary
                    inner_list.append(max(sa2_populations, key=lambda x: x[1])[0]) # SA2 area code
                    inner_list.append(max(sa2_populations, key=lambda x: x[1])[1]) # total population of SA2 area
                    inner_list.append(max(sa2_populations, key=lambda x: x[1])[2]) # standard deviation of populations within the SA2 area
                    inner_dict[code] = inner_list
                
                # assumption made: based on example outputs from guidelines, inner dictionaries were sorted by the populations of each SA2 area (descending)
                sorted_inner = dict(sorted(inner_dict.items(), key=lambda x: -x[1][1]))
                
                # creation of output dictionary for OP2
                outer_dict[num] = sorted_inner
        
        return outer_dict
    
    OP2 = state_population_stats()
    
    def cosine_similarity(A, B):
        """Calculates cosine similarity from two given arguments"""
        
        # performs the cosine similarity formula, step by step
        numerator = sum(A * B for A, B in zip(A, B))
        mag_A = sum(a ** 2 for a in A) ** 0.5
        mag_B = sum(b ** 2 for b in B) ** 0.5
        denominator = mag_A * mag_B
        # prevention of division by zero
        if denominator != 0:
            cos_sim = numerator / denominator
        else:
            cos_sim = 0
        return cos_sim
    
    def max_similarity_per_sa3():
        """Creates a dictionary using SA3 area names as keys and its two SA2 areas sharing the greatest similarity"""
        
        output_dict = {}
        
        for num in sa3_codes:
            sa2_populations = {}
            for row in values2[1:]:
                if row[sa2_code_index_p].startswith(num) and row[sa2_name_index_p] not in sa2_populations.keys():
                    sa2_list = []
                    for column in row:
                        if column != row[sa2_code_index_p] and column != row[sa2_name_index_p]:
                            sa2_list.append(int(column))
                    sa2_populations[row[sa2_name_index_p]] = sa2_list

            # only gets SA3 areas with at least 15 SA2 areas
            if len(sa2_populations.items()) >= 15:
                                
                sa2_percentages = {}
                for sa2_name, population in sa2_populations.items():
                    total = sum(population)
                    # prevention of division by zero
                    if total != 0:
                        percentages = [num / total for num in population]
                    else:
                        continue
                    sa2_percentages[sa2_name] = percentages
                
                sa2_names = sorted(sa2_percentages.keys()) # arranges SA2 area names alphabetically for output_value list later
                
                # tests every possible combination of SA2 areas for cosine similarity
                max_similarity_pair = []
                max_score = 0.0
                for x in range(len(sa2_names)):
                    for y in range(x + 1, len(sa2_names)):
                        sa2_a = sa2_names[x]
                        sa2_b = sa2_names[y]
                        A = sa2_percentages[sa2_a]
                        B = sa2_percentages[sa2_b]
                        similarity = cosine_similarity(A, B)
                        
                        # constantly replaces the maximum similarity pair, until the true maximum is reached
                        if similarity > max_score:
                            max_score = similarity
                            max_similarity_pair = [sa2_a, sa2_b]
                
                # arranges the output value: the two SA2 areas with the highest cosine similarity (arranged alphabetically), and the similarity score itself rounded to 4 decimal places
                output_value = [max_similarity_pair[0], max_similarity_pair[1], round(max_score, 4)]
                
                # creation of output dictionary for OP3
                for row in values1[1:]:
                    if num == row[sa3_code_index] and row[sa3_name_index] not in output_dict.keys():
                        output_dict[row[sa3_name_index]] = output_value
                
        return output_dict
    
    OP3 = max_similarity_per_sa3()

    return OP1, OP2, OP3

if __name__ == "__main__":

    from pprint import pprint

    # filenames and pprint statements hardcoded to display sample data
    OP1,OP2,OP3 = main('SampleData_Areas.csv', 'SampleData_Populations.csv')

    print("OP1:\n")
    pprint(OP1)
    print("\nOP2:\n")
    pprint(OP2)
    print("\nOP3:\n")
    pprint(OP3)

"""
Debugging Documentation:

Issue 1 (Date 2025 May 19):

- Error Description:
    ValueError: invalid literal for int() with base 10: 'abc'
    
- Erroneous Code Snippet:
    population_sum += int(column)

- Test Case:
    OP1, OP2, OP3 = main('SampleData_Areas_P2.csv', 'SampleData_Populations_P2_test.csv')
    # project file values were adjusted to check for edge cases
    # one of the values in the populations file was changed to 'abc' in this case
    
- Reflection:
     Realised non-numeric strings (including decimals) in population columns caused a ValueError due to an attempt to convert
     to an integer. To fix this, I used a try-except block to skip the row if the error occurred. Learned to anticipate and
     filter out unexpected formats in data input.

Issue 2 (Date 2025 May 20):

- Error Description:
    ZeroDivisionError: division by zero
    
- Erroneous Code Snippet:
    if total_count != 0:
        st_dev = (sd_summation / (total_count - 1)) ** 0.5
    else:
        st_dev = 0

- Test Case:
    OP1, OP2, OP3 = main('SampleData_Areas_P2.csv', 'SampleData_Populations_P2_test.csv')
    
    # variable values were adjusted to check for edge cases
    total_count = 1
    
- Reflection:
    In an attempt to prevent a ZeroDivisionError, I added a conditional to attempt division only if total_count was not equal to 0.
    However, I did not realise the formula used actually subtracted total_count by 1. I fixed this simply by adjusting the value of
    total_count in the conditional to be != 1 instead. Learned to always check if the values in the conditional align with its purpose.
    
Issue 3 (Date 2025 May 20):

- Error Description:
    ValueError: max() arg is an empty sequence
    
- Erroneous Code Snippet:
    sa2_populations = []
    for num in sa2_codes:
        for row in values2[1:]:
            if num == row[sa2_code_index_p]:
                sa2_populations.append((row[sa2_name_index_p], int(row[i])))
        max_sa2_name = max(sa2_populations, key=lambda x: x[1])[0]

- Test Case:
    OP1, OP2, OP3 = main('SampleData_Areas_P2.csv', 'SampleData_Populations_P2_test.csv')
    
    # multiple rows in the SampleData_Populations_P2.csv file were deleted to see if program could handle missing data
    
- Reflection:
    While checking for edge cases, I realised my program could not handle cases with missing data. To fix this, both files were matched
    1 to 1 before any calculations took place to avoid mismatching or out-of-range indexing. Learned to consider how missing data can
    affect my code (mismatching, indexing, etc).

"""