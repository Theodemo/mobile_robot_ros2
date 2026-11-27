#include "main.h"
#include <stdlib.h>
#define VITESSE_CAM 400

#include "motorCommand.h"
#include "pidFilter.h"
#include "quadEncoder.h"
#include "captDistIR.h"
#include "VL53L0X.h"
#include "groveLCD.h"

#define ARRAY_LEN 100
#define SAMPLING_PERIOD_ms 5
#define USE_MOTOR 1

//################################################
#define EX1 1
#define EX2 2
#define EX3 3

#define SYNCHRO_EX EX4
//################################################
//################################################
// PARAMETRE A MODIFIER EN FONCTION DU N° ROBOT
#define ROS_DOMAIN_ID 1
//################################################
extern UART_HandleTypeDef huart1;
extern UART_HandleTypeDef huart2;
extern DMA_HandleTypeDef hdma_usart1_rx;
extern DMA_HandleTypeDef hdma_usart1_tx;
extern DMA_HandleTypeDef hdma_usart2_rx;
extern DMA_HandleTypeDef hdma_usart2_tx;

extern I2C_HandleTypeDef hi2c1;

/* Definitions for defaultTask */
osThreadId_t defaultTaskHandle;
const osThreadAttr_t defaultTask_attributes = {
  .name = "defaultTask",
  .stack_size = 3000 * 4,
  .priority = (osPriority_t) osPriorityNormal,
};

// Déclaration des objets synchronisants !! Ne pas oublier de les créer
xSemaphoreHandle xSemaphore = NULL;
xQueueHandle qh = NULL;
xQueueHandle qh_rear_reaction = NULL;
xQueueHandle qh_front_reaction = NULL;
xQueueHandle qh_mode_show = NULL;

struct AMessage // Exemple de type de message
{
	char command;
	int data;
};

struct MotorMessage
{
	float left_data;
	float right_data;
};

struct ModeMessage
{
	int mode;
	// mode = 0, random
	// mode = 1, line
	// mode = 2, controlled
};


void SystemClock_Config(void);
void microros_task(void *argument);
uint16_t mes_vl53=0;

int Left_first_index_reached = 0;
int Right_first_index_reached = 0;

//========================================================================
#if SYNCHRO_EX == EX1

int tab_speed[100];

static void task_A(void *pvParameters)
{
int speed=0;
static int i = 0;

	for (;;)
	{
		HAL_GPIO_WritePin(GPIOB, GPIO_PIN_4, 1);

		mes_vl53 = VL53L0X_readRangeContinuousMillimeters();


		motorLeft_SetDuty(150);
		speed = quadEncoder_GetSpeedL();

		if (i < 100)
		{
		tab_speed[i]= speed;
		i++;
		}

		HAL_GPIO_WritePin(GPIOB, GPIO_PIN_4, 0);
		vTaskDelay(5);
	}
}
/*
static void task_B(void *pvParameters)
{
int i=0;

for (;;)
	{
		i++;
	}
}*/
//========================================================
#elif SYNCHRO_EX == EX2

static void task_C( void *pvParameters )
{
	for (;;)
	{
		 printf("TASK C \n\r");
		xSemaphoreTake( xSemaphore, portMAX_DELAY );
	}
}

static void task_D( void *pvParameters )
{
	for (;;)
	{
		 printf("TASK D \n\r");
		xSemaphoreGive( xSemaphore );
		vTaskDelay(1000);
	}
}

//========================================================
#elif SYNCHRO_EX == EX3

static void task_E( void *pvParameters )
{
	struct AMessage pxMessage;
	pxMessage.command='a';
	pxMessage.data=10;
	vTaskDelay(1000);
	for (;;)
	{
		HAL_GPIO_WritePin(GPIOB, GPIO_PIN_4, 1);
	    printf("TASK E \r\n");
		xQueueSend( qh, ( void * ) &pxMessage,  portMAX_DELAY );
		xSemaphoreTake( xSemaphore, portMAX_DELAY );

		HAL_GPIO_WritePin(GPIOB, GPIO_PIN_4, 0);
		vTaskDelay(SAMPLING_PERIOD_ms);

	}
}

static void task_F(void *pvParameters)
{
	struct AMessage pxRxedMessage;

	for (;;)
	{
		xQueueReceive( qh,  &( pxRxedMessage ) , portMAX_DELAY );
		 printf("TASK F \r\n");
		xSemaphoreGive( xSemaphore );
	}
}
#endif

//==========================================
//	Task asservissement
//==========================================


static void task_pid(void *pvParameters)
{

	float pid_right = 0.0f;
	float pid_left = 0.0f;

	int16_t speedR = 0;
	int16_t speedL = 0;

	vTaskDelay(1000);
	for (;;)
	{
		speedR = quadEncoder_GetSpeedR();
		speedL = quadEncoder_GetSpeedL();

		//calculate the pid response
		 pid_right = pidFilter_ComputeRight(speedR);
		 pid_left = pidFilter_ComputeLeft(speedL);
		 //printf("PID Right | PID Left : %f | %f \r\n", pid_right, pid_left);


		 	/*printf("SPEED L16 | R16 : %i | %i\n\r",
		 	    		(int)(speedL),
		 				(int)(speedR)
		 				);*/

		motorLeft_SetDuty(voltage2duty(pid_left));
		motorRight_SetDuty(voltage2duty(pid_right));

		vTaskDelay(5);
	}
}

static void task_dist_acq()
{
	struct MotorMessage pxFrontMessage;
	pxFrontMessage.left_data=0;
	pxFrontMessage.right_data=0;

	struct MotorMessage pxRearMessage;
	pxFrontMessage.left_data=0;
	pxFrontMessage.right_data=0;

	int table[2];
	uint16_t vl53_dist = 0;
	int new_command[2] = {0,0};

	int isRearClose = 0;
	int isFrontClose = 0;


	for (;;)
	{
		captDistIR_Get(table);
		printf("ADC DISTANCE : L%i | R%i \n\r", table[1], table[0]);
		vl53_dist = VL53L0X_readRangeContinuousMillimeters();
		//printf("I2C DISTANCE : %i\n\r", vl53_dist);
		if (vl53_dist < 200)
		{
			new_command[0] += 1000;
			new_command[1] += 1000;

		}
		if ( (table[0] > 1800) && (table[1] > 1800) )
		{
			new_command[0] -= 1000;
			new_command[1] -= 1000;
		}
		else if (table[0] > 1800)
		{
			new_command[0] -= 1000;
		}
		else if (table[1] > 1800)
		{
			new_command[1] -= 1000;

		}
		if ((new_command[1] < 0) || (new_command[0] < 0))
		{
			pxRearMessage.left_data=(float)(new_command[1]);
			pxRearMessage.right_data=(float)(new_command[0]);
			xQueueSend( qh_rear_reaction, ( void * ) &pxRearMessage,  portMAX_DELAY );
			pxRearMessage.left_data = 0;
			pxRearMessage.right_data = 0;
		}
		if ((new_command[1] > 0) || (new_command[0] > 0))
		{
			pxFrontMessage.left_data=(float)(new_command[1]);
			pxFrontMessage.right_data=(float)(new_command[0]);
			xQueueSend( qh_front_reaction, ( void * ) &pxFrontMessage,  portMAX_DELAY );
			pxFrontMessage.left_data = 0;
			pxFrontMessage.right_data = 0;
		}
		new_command[0] = 0;
		new_command[1] = 0;


		vTaskDelay(100);

	}
}


static void task_rear_reaction()
{
	struct MotorMessage pxRxedMessage;

	float old_command[2] = {0.0f, 0.0f};
	float new_command[2] = {0.0f, 0.0f};


	for (;;)
	{
		xQueueReceive( qh_rear_reaction,  &( pxRxedMessage ) , portMAX_DELAY );
		new_command[0] = pxRxedMessage.right_data;
		new_command[1] = pxRxedMessage.left_data;
		printf("NEW COMMAND REAR: %f | %f\n\r", new_command[1], new_command[0]);
		old_command[1] = pidFilter_GetCommandLeft();
		old_command[0] = pidFilter_GetCommandRight();
		pidFilter_SetCommandLeft(new_command[1]);
		pidFilter_SetCommandRight(new_command[0]);
		vTaskDelay(100);
		pidFilter_SetCommandLeft(old_command[1]);
		pidFilter_SetCommandRight(old_command[0]);

	}
}

static void task_front_reaction()
{
	struct MotorMessage pxRxedMessage;

	float old_command[2] = {0.0f, 0.0f};
	float new_command[2] = {0.0f, 0.0f};

	for (;;)
	{
		xQueueReceive( qh_front_reaction,  &( pxRxedMessage ) , portMAX_DELAY );
		new_command[0] = pxRxedMessage.right_data;
		new_command[1] = pxRxedMessage.left_data;
		printf("NEW COMMAND FRONT: %f | %f\n\r", new_command[1], new_command[0]);
		old_command[1] = pidFilter_GetCommandLeft();
		old_command[0] = pidFilter_GetCommandRight();
		pidFilter_SetCommandLeft(new_command[1]);
		pidFilter_SetCommandRight(new_command[0]);
		vTaskDelay(100);
		pidFilter_SetCommandLeft(old_command[1]);
		pidFilter_SetCommandRight(old_command[0]);
	}
}

static void task_write_mode()
{
	struct ModeMessage pxRxedMessage;
	int mode;

	for (;;)
	{
		xQueueReceive( qh_mode_show,  &( pxRxedMessage ) , portMAX_DELAY );
		mode = pxRxedMessage.mode;
		if (mode == 0) //random
		{
			groveLCD_setCursor(0,0);
			groveLCD_term_printf("RANDOM\n\r");
		}
		else if (mode == 1) //line
		{
			groveLCD_setCursor(0,0);
			groveLCD_term_printf("LIGNE\n\r");
		}
		else if (mode == 2) //controlled
		{
			groveLCD_setCursor(0,0);
			groveLCD_term_printf("CONTROLE\n\r");
		}
		vTaskDelay(50);
	}
}

static void task_change_mode()
{
	for (;;)
	{

	}
}

static void task_random_mode()
{
	vTaskDelay(1000);

	struct ModeMessage pxMessage;

	int Nmax = 3000;
	int NHalfMax = 0;

	float left_value = 0;
	float right_value = 0;
	xQueueSend( qh_mode_show, ( void * ) &pxMessage,  portMAX_DELAY );
	for (;;)
	{
		left_value = (float)(rand() % (Nmax + 1) - NHalfMax);
		right_value = (float)(rand() % (Nmax + 1) - NHalfMax);

		pidFilter_SetCommandLeft(left_value);
		pidFilter_SetCommandRight(right_value);
		vTaskDelay(5000);
	}
}

//=========================================================================
int main(void)
{
  int ret=0;
  int tab_dist[2];

  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();
  MX_DMA_Init();
  MX_USART1_UART_Init();
  MX_USART2_UART_Init();
  MX_I2C1_Init();

  motorCommand_Init();
  quadEncoder_Init();
  captDistIR_Init();
  pidFilter_Init();

  HAL_Delay(500);


  // Affichage via UART2 sur Terminal série $ minicom -D /dev/ttyACM0
  printf("hello\r\n"); // REM : ne pas oublier le \n

  VL53L0X_init();

  ret = VL53L0X_validateInterface();
  if(ret ==0)
  {
	  printf("VL53L0X OK\r\n");
  }
  else
  {
	  printf("!! PROBLEME VL53L0X !!\r\n");
  }
  VL53L0X_startContinuous(0);


  int a, b;
  groveLCD_begin(16,2,0); // !! cette fonction prend du temps
  HAL_Delay(100);
  groveLCD_display();
  a=5; b=2;
  groveLCD_term_printf("%d+%d=%d",a,b,a+b);
  groveLCD_setCursor(0,0);
  groveLCD_term_printf("hello");


  HAL_Delay(50);


#if USE_MOTOR

  int16_t speed=0;
// RECHERCHE DE LA POSITION INITIALE ( 1er signal 'index' du capteur )
	Left_first_index_reached = 0;
	 while( Left_first_index_reached != 1 )
	 {
		motorLeft_SetDuty(130);
		HAL_Delay(SAMPLING_PERIOD_ms);
		speed = quadEncoder_GetSpeedL();
	 }

	Right_first_index_reached = 0;
	 while( Right_first_index_reached != 1 )
	 {
		motorRight_SetDuty(130);
		HAL_Delay(SAMPLING_PERIOD_ms);
		speed = quadEncoder_GetSpeedR();
	 }

	 motorLeft_SetDuty(100);
	 motorRight_SetDuty(100);
	 HAL_Delay(200);

	 speed = quadEncoder_GetSpeedL();
	 speed = quadEncoder_GetSpeedR();
#endif

  osKernelInitialize();

  xTaskCreate( microros_task, ( const portCHAR * ) "microros_task", 3000 /* stack size */, NULL,  24, NULL );
#if SYNCHRO_EX == EX1
	xTaskCreate( task_A, ( const portCHAR * ) "task A", 128 /* stack size */, NULL, 26, NULL );
	xTaskCreate( task_B, ( const portCHAR * ) "task B", 128 /* stack size */, NULL, 25, NULL );
#elif SYNCHRO_EX == EX2
	xTaskCreate( task_C, ( signed portCHAR * ) "task C", 128 /* stack size */, NULL, 28, NULL );
	xTaskCreate( task_D, ( signed portCHAR * ) "task D", 128 /* stack size */, NULL, 27, NULL );
#elif SYNCHRO_EX == EX3
	xTaskCreate( task_E, ( signed portCHAR * ) "task E", 128 /* stack size */, NULL, 30, NULL );
	xTaskCreate( task_F, ( signed portCHAR * ) "task F", 128 /* stack size */, NULL, 29, NULL );
#endif

	//xTaskCreate( task_pid1, ( signed portCHAR * ) "task E", 128 /* stack size */, NULL, 32, NULL );
	xTaskCreate( task_pid, ( signed portCHAR * ) "task F", 256 /* stack size */, NULL, 31, NULL );
	xTaskCreate( task_dist_acq, ( signed portCHAR * ) "task F", 256 /* stack size */, NULL, 27, NULL );
	xTaskCreate( task_rear_reaction, ( signed portCHAR * ) "task F", 256 /* stack size */, NULL, 25, NULL );
	xTaskCreate( task_front_reaction, ( signed portCHAR * ) "task F", 256 /* stack size */, NULL, 26, NULL );
	xTaskCreate( task_random_mode, ( signed portCHAR * ) "task F", 256 /* stack size */, NULL, 32, NULL );
	xTaskCreate( task_write_mode, ( signed portCHAR * ) "task F", 256 /* stack size */, NULL, 32, NULL );

	vSemaphoreCreateBinary(xSemaphore);
	xSemaphoreTake( xSemaphore, portMAX_DELAY );

	qh = xQueueCreate( 1, sizeof(struct AMessage ) );

	//Queue for motor reactions
	qh_rear_reaction = xQueueCreate( 1, sizeof(struct MotorMessage ) );
	qh_front_reaction = xQueueCreate( 1, sizeof(struct MotorMessage ) );
	qh_mode_show = xQueueCreate( 1, sizeof(struct ModeMessage));

  osKernelStart();

  while (1)
  {}

}
//=========================================================================
bool cubemx_transport_open(struct uxrCustomTransport * transport);
bool cubemx_transport_close(struct uxrCustomTransport * transport);
size_t cubemx_transport_write(struct uxrCustomTransport* transport, const uint8_t * buf, size_t len, uint8_t * err);
size_t cubemx_transport_read(struct uxrCustomTransport* transport, uint8_t* buf, size_t len, int timeout, uint8_t* err);

void * microros_allocate(size_t size, void * state);
void microros_deallocate(void * pointer, void * state);
void * microros_reallocate(void * pointer, size_t size, void * state);
void * microros_zero_allocate(size_t number_of_elements, size_t size_of_element, void * state);


void subscription_callback(const void * msgin)
{
  const std_msgs__msg__String * msg = (const std_msgs__msg__String *)msgin;

  // Process message
  printf("Received from HOST: %s\n\r", msg->data);
}


void microros_task(void *argument)
{
  rmw_uros_set_custom_transport( true, (void *) &huart1, cubemx_transport_open,  cubemx_transport_close,  cubemx_transport_write, cubemx_transport_read);

  rcl_allocator_t freeRTOS_allocator = rcutils_get_zero_initialized_allocator();
  freeRTOS_allocator.allocate = microros_allocate;
  freeRTOS_allocator.deallocate = microros_deallocate;
  freeRTOS_allocator.reallocate = microros_reallocate;
  freeRTOS_allocator.zero_allocate =  microros_zero_allocate;

  if (!rcutils_set_default_allocator(&freeRTOS_allocator)) {
      printf("Error on default allocators (line %d)\n", __LINE__);
  }

  // micro-ROS app
  rclc_support_t support;
  rcl_allocator_t allocator;
  allocator = rcl_get_default_allocator();

  // create node
  rcl_node_t node;
  rcl_node_options_t node_ops = rcl_node_get_default_options();
  rcl_init_options_t init_options = rcl_get_zero_initialized_init_options();
  rcl_init_options_init(&init_options, allocator);
  rcl_init_options_set_domain_id(&init_options, ROS_DOMAIN_ID);

  rclc_support_init_with_options(&support, 0, NULL, &init_options, &allocator);
  rclc_node_init_default(&node, "STM32_Node","", &support);

  // create publisher
  rcl_publisher_t publisher;
  std_msgs__msg__String sensor_dist_back_msg;
  rclc_publisher_init_default(&publisher, &node, ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, String),"/sensor/dist_back");

  // create subscriber
  rcl_subscription_t subscriber;
  std_msgs__msg__String str_msg;
  rclc_subscription_init_default(&subscriber,&node,ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, String),"/command/move");
  // Add subscription to the executor
  rclc_executor_t executor;
  rclc_executor_init(&executor, &support.context, 1, &allocator); // ! 'NUMBER OF HANDLES' A MODIFIER EN FONCTION DU NOMBRE DE TOPICS
  rclc_executor_add_subscription(&executor, &subscriber, &str_msg, &subscription_callback, ON_NEW_DATA);

  str_msg.data.data = (char * ) malloc(ARRAY_LEN * sizeof(char));
  str_msg.data.size = 0;
  str_msg.data.capacity = ARRAY_LEN;

  for(;;)
  {
	  sprintf(str_msg.data.data, "from STM32 : mes_vl53 : #%d", (int32_t)mes_vl53);
	  str_msg.data.size = strlen(str_msg.data.data);

      rcl_ret_t ret = rcl_publish(&publisher, &str_msg, NULL);

		if (ret != RCL_RET_OK)
		{
		  printf("Error publishing (line %d)\n\r", __LINE__);
		}
    rclc_executor_spin_some(&executor, RCL_MS_TO_NS(10));
    osDelay(10);
  }
}
//=========================================================================
/**
  * @brief  Period elapsed callback in non blocking mode
  * @note   This function is called  when TIM1 interrupt took place, inside
  * HAL_TIM_IRQHandler(). It makes a direct call to HAL_IncTick() to increment
  * a global variable "uwTick" used as application time base.
  * @param  htim : TIM handle
  * @retval None
  */
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
  if (htim->Instance == TIM4)
  {
    HAL_IncTick();
  }
}
//=========================================================================
void Error_Handler(void)
{
  __disable_irq();
  while (1)
  {}
}
//=========================================================================
#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
