import re
from decimal import Decimal
from typing import Union


class MathHelper:
    @classmethod
    def round(cls, num: Union[int, float, Decimal], decimal_place: int = 0):
        # Get the type of given number
        type_num = type(num)
        # If the given type is not a valid number type, raise TypeError
        if type_num not in [int, float, Decimal]:
            raise TypeError("type {} doesn't define __round__ method".format(type_num.__name__))
        # If passed number is int, there is no rounding off.
        if type_num == int:
            return num
        # Convert number to string.
        str_num = str(num).lower()
        # We will remove negative context from the number and add it back in the end
        negative_number = False
        if num < 0:
            negative_number = True
            str_num = str_num[1:]
        # If number is in format 1e-12 or 2e+13, we have to convert it to
        # to a string in standard decimal notation.
        if 'e-' in str_num:
            # For 1.23e-7, e_power = 7
            e_power = int(re.findall('e-[0-9]+', str_num)[0][2:])
            # For 1.23e-7, number = 123
            number = ''.join(str_num.split('e-')[0].split('.'))
            zeros = ''
            # Number of zeros = e_power - 1 = 6
            for i in range(e_power - 1):
                zeros = zeros + '0'
            # Scientific notation 1.23e-7 in regular decimal = 0.000000123
            str_num = '0.' + zeros + number
        if 'e+' in str_num:
            # For 1.23e+7, e_power = 7
            e_power = int(re.findall('e\+[0-9]+', str_num)[0][2:])
            # For 1.23e+7, number_characteristic = 1
            # characteristic is number left of decimal point.
            number_characteristic = str_num.split('e+')[0].split('.')[0]
            # For 1.23e+7, number_mantissa = 23
            # mantissa is number right of decimal point.
            number_mantissa = str_num.split('e+')[0].split('.')[1]
            # For 1.23e+7, number = 123
            number = number_characteristic + number_mantissa
            zeros = ''
            # Eg: for this condition = 1.23e+7
            if e_power >= len(number_mantissa):
                # Number of zeros = e_power - mantissa length = 5
                for i in range(e_power - len(number_mantissa)):
                    zeros = zeros + '0'
                # Scientific notation 1.23e+7 in regular decimal = 12300000.0
                str_num = number + zeros + '.0'
            # Eg: for this condition = 1.23e+1
            if e_power < len(number_mantissa):
                # In this case, we only need to shift the decimal e_power digits to the right
                # So we just copy the digits from mantissa to characteristic and then remove
                # them from mantissa.
                for i in range(e_power):
                    number_characteristic = number_characteristic + number_mantissa[i]
                number_mantissa = number_mantissa[i:]
                # Scientific notation 1.23e+1 in regular decimal = 12.3
                str_num = number_characteristic + '.' + number_mantissa
        # characteristic is number left of decimal point.
        characteristic_part = str_num.split('.')[0]
        # mantissa is number right of decimal point.
        mantissa_part = str_num.split('.')[1]
        # If number is supposed to be rounded to whole number,
        # check first decimal digit. If more than 5, return
        # characteristic + 1 else return characteristic
        if decimal_place == 0:
            if mantissa_part and int(mantissa_part[0]) >= 5:
                return type_num(int(characteristic_part) + 1)
            return type_num(characteristic_part)
        # Get the decimal_place of the given number.
        num_decimal_place = len(mantissa_part)
        # Rounding off is done only if number decimal_place is
        # greater than requested decimal_place
        if num_decimal_place <= decimal_place:
            return num
        # Replace the last '5' with 6 so that rounding off returns desired results
        if str_num[-1] == '5':
            str_num = re.sub('5$', '6', str_num)
        result = round(type_num(str_num), decimal_place)
        # If the number was negative, add negative context back
        if negative_number:
            result = result * -1

        return result
