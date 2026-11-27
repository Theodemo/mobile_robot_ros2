/*
 * filter.h
 *
 *  Created on: Apr 7, 2024
 *      Author: Madec
 */

#ifndef INC_PIDFILTER_H_
#define INC_PIDFILTER_H_

#include "main.h"
//====================================================================
//			PID
//====================================================================

extern volatile float Kp;
extern volatile float Kd;
extern volatile float Ki;
//extern volatile uint32_t te_ms;
extern volatile float LOe_k[3];
extern volatile float LUc_k[2];
extern volatile float Lcommand;

extern volatile float ROe_k[3];
extern volatile float RUc_k[2];
extern volatile float Rcommand;

extern volatile float debug_tension;

void pidFilter_Init(void);

float pidFilter_GetCommandRight(void);
float pidFilter_GetCommandLeft(void);

void pidFilter_SetKp(float new_Kp);

void pidFilter_SetKi(float new_Ki);

void pidFilter_SetKd(float new_Kd);

void pidFilter_SetCommandLeft(float new_command);

void pidFilter_SetCommandRight(float new_command);


void pidFilter_SetCommandLeftVoltage(float new_voltage);

void pidFilter_SetCommandRightVoltage(float new_voltage);

float pidFilter_ComputeLeft(int16_t output_speed);

float pidFilter_ComputeRight(int16_t output_speed);

#endif /* INC_PIDFILTER_H_ */
