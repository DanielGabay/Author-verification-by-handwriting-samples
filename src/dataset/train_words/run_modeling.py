import modeling



def main():

    # this is the order of the arguments ---> run_model(num_of_epochs, train_size, test_size, batch_Size, model_number, filters, dropout, model_number)
    model_name = "words_shuffle_model_resized_80_120"
    print("-----------------------------------------------------------------")
    print("------------------------------------------------------------------")
    print(model_name)
    
    modeling.run_model(10, train_size=20900, validation_size=825, batch_Size=64, filters=8, dropout=0.1, kernel=7, model_name=model_name)


if __name__ == '__main__':
        main()
